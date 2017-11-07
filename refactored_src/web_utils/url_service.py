import logging
import re
from psycopg2.extensions import TransactionRollbackError
from time import sleep
from random import randint

from .slug_list_factory import SlugListFactory
from .no_such_slug import NoSuchSlug
from .slug_already_in_use import SlugAlreadyInUse
from .slug_list import SlugList
from ..feed_utils.no_such_show_error import NoSuchShowError


logger = logging.getLogger(__name__)


class UrlService:

    split_on_non_word = re.compile(r"(?:[^\w\d]|_)+")

    def __init__(self, db_settings, show_source):
        self.slug_list_factory = SlugListFactory(db_settings)
        self.show_source = show_source

    def get_canonical_slug_for_slug(self, slug: str, level=0, connection=None):
        """Get the slug which shall be used for the given slug.

        Args:
            slug (str): The slug which we shall find the canonical slug for.

        Returns:
            (int, str): Tuple containing the Digas ID and the canonical slug which
                should be used (instead of the given slug).

        Raises:
            NoSuchShowError: If no show matches the given slug.
        """

        # Normalize
        slug = slug.strip().lower()
        sluglist = None
        connection_provided = connection is not None
        connection = connection or self.slug_list_factory.create_connection()
        try:
            try:
                sluglist = self.slug_list_factory.from_slug(slug, connection)
                self.invalidate_list_of_shows_if_old(sluglist)
                stored_canonical_slug = sluglist.canonical_slug
                actual_canonical_slug = self.create_slug_for(sluglist.digas_id)

                if stored_canonical_slug != actual_canonical_slug:
                    # This show has gotten a new name
                    logger.info("Change in slug: %s shall redirect to %s",
                                stored_canonical_slug,
                                actual_canonical_slug)
                    try:
                        sluglist.canonical_slug = actual_canonical_slug
                    except SlugAlreadyInUse as e:
                        # Another show is using the slug this show is trying to use
                        # Notify radioteknisk
                        logger.error(
                            "The slug %s is already in use by another show (%s)"
                            ". Falling back to previous slug, %s. "
                            "Pick another name for the show; you may confuse "
                            "listeners.",
                            actual_canonical_slug,
                            e,
                            stored_canonical_slug
                        )
                if not connection_provided:
                    sluglist.commit()
                return sluglist.digas_id, sluglist.canonical_slug

            except NoSuchSlug:
                # There is no record of this slug in the database.
                # Is it an actual slug for a show, or is this a 404?
                digas_id = self.get_show_with_slug(slug)
                # No exception, so there is a show with this slug.
                # (Additional note about multiple instances of PodcastFeedGenerator:
                #   A change in show name won't be applied before a new instance of
                #   PodcastFeedGenerator is created, and then queried about the URL
                #   of the show. Once that happens, the new slug is put into the DB
                #   and any existing instances will notice that their list of shows
                #   is out of date when queried about that show's URL. Before that
                #   happens, there will be a timeframe in which the show's canonical
                #   URL gives 404 (between the name changing, and a new
                #   PodcastFeedGenerator instance being asked about the show's URL.)
                # (If you want to make sure a new URL works, you can create a new
                #   instance of PodcastFeedGenerator and call
                #   get_canonical_slug_for_slug with the new PodcastFeedGenerator
                #   instance.)

                try:
                    # Assuming the show already is present in the database
                    sluglist = self.slug_list_factory.from_id(digas_id, connection)
                    logger.info("Change in slug: %s shall redirect to %s",
                                sluglist.canonical_slug,
                                slug)
                    sluglist.canonical_slug = slug
                except NoSuchSlug:
                    # Nope, add it in the database.
                    sluglist = self.slug_list_factory.create(digas_id, slug, connection=connection)
                    logger.info("Adding slug %s (Digas ID %s) to the database",
                                slug,
                                digas_id)
                    sluglist.persist()
                if not connection_provided:
                    sluglist.commit()
                return sluglist.digas_id, sluglist.canonical_slug

        except TransactionRollbackError:
            logger.debug("Transaction was rolled back")
            # Someone has probably beat us to the punch
            if sluglist:
                connection.close()
            # Should we give up?
            if level >= 10 or connection_provided:
                if level >= 10:
                    logger.error(
                        "Transaction has been rolled back 10 times, giving up"
                    )
                raise
            # I don't know if we need this, but randomize how long we sleep, so two
            # instances won't bash their heads against each other forever
            sleep(randint(0, 2**level) / 100)
            # Try again; should work in most cases
            return self.get_canonical_slug_for_slug(
                slug,
                level + 1
            )

        except:
            if not connection_provided:
                connection.rollback()
                connection.close()
            raise

    def invalidate_list_of_shows_if_old(
            self,
            sluglist: SlugList
    ):
        fetched_at = self.show_source.last_fetched
        last_modified_at = sluglist.last_modified

        if fetched_at is None:
            return

        if fetched_at < last_modified_at:
            if self.show_source.get_show_names:
                del self.show_source.get_show_names
            if self.show_source.shows:
                del self.show_source.shows
        return

    def create_slug_for(self, digas_id: int) -> str:
        """Create slug for the given show, using the show's name.

        Args:
            digas_id (int): The Digas ID of the show we shall create the slug for.

        Returns:
            str: The slug which the given show shall have.
        """
        try:
            show = self.show_source.shows[digas_id]
        except KeyError as e:
            raise NoSuchShowError(digas_id) from e
        return self.sluggify(show.name)

    @classmethod
    def sluggify(cls, name: str) -> str:
        """Creates a slug out of the given show name.

        Args:
            name (str): The name which we shall make a slug out of.

        Returns:
            str: name, converted into a URL- and human-friendly slug.
        """
        return "-".join([word for word in cls.split_on_non_word.split(name.strip().lower()) if word])

    def get_show_with_slug(self, slug: str) -> int:
        """Return the digas ID of the show whose actual slug equals the given slug.

        Args:
            slug (str): The slug the resulting show shall have.

        Returns:
            int: The Digas ID of the show with the given slug.

        Raises:
            NoSuchShowError: If there is no matching show.
        """
        shows = self.show_source.get_show_names
        show_slugs = \
            {
                self.sluggify(show.name): show
                for name, show in shows.items()
            }
        try:
            return show_slugs[slug].id
        except KeyError as e:
            raise NoSuchShowError from e
