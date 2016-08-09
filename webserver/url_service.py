import logging
import re

from generator.generate_feed import PodcastFeedGenerator
from .slug_list import SlugList
from .no_such_slug import NoSuchSlug
from .slug_already_in_use import SlugAlreadyInUse
from generator import NoSuchShowError


logger = logging.getLogger(__name__)


def get_canonical_slug_for_slug(slug: str) -> str:
    """Get the slug which shall be used for the given slug.

    Args:
        slug (str): The slug which we shall find the canonical slug for.

    Returns:
        str: The canonical slug which should be used (instead of the given
            slug).

    Raises:
        NoSuchShowError: If no show matches the given slug.
    """

    # Normalize
    slug = slug.strip().lower()
    sluglist = None
    try:
        sluglist = SlugList.from_slug(slug)
        stored_canonical_slug = sluglist.canonical_slug
        actual_canonical_slug = create_slug_for(sluglist.digas_id)

        if stored_canonical_slug != actual_canonical_slug:
            # This show has gotten a new name
            try:
                sluglist.canonical_slug = actual_canonical_slug
            except SlugAlreadyInUse:
                # Another show is using the slug this show is trying to use
                # Notify radioteknisk
                logger.critical(
                    "The slug %s is already in use by another show (with"
                    "canonical slug %s). Falling back to previous slug, %s. "
                    "Pick another name for the show; you may confuse "
                    "listeners.",
                    actual_canonical_slug,
                    get_canonical_slug_for_slug(actual_canonical_slug),
                    stored_canonical_slug
                )
        return sluglist.canonical_slug
    except NoSuchSlug:
        # There is no record of this slug in the database.
        # Is it an actual slug for a show, or is this a 404?
        digas_id = get_show_with_slug(slug)

        # No exception, so there is a show with this slug.
        # Add it in the database.
        sluglist = SlugList(digas_id, slug)
        sluglist.persist()
    except:
        if sluglist:
            sluglist.abort()
            # Make sure sluglist isn't committed by the finally block
            sluglist = None
        raise
    finally:
        if sluglist:
            sluglist.commit()


def create_slug_for(digas_id: int) -> str:
    """Create slug for the given show, using the show's name.

    Args:
        digas_id (int): The Digas ID of the show we shall create the slug for.

    Returns:
        str: The slug which the given show shall have.
    """
    gen = PodcastFeedGenerator(quiet=True)
    show = gen.show_source.shows[digas_id]
    return sluggify(show.name)


remove_non_word = re.compile(r"[^\w\d]|_")


def sluggify(name: str) -> str:
    """Creates a slug out of the given show name.

    Args:
        name (str): The name which we shall make a slug out of.

    Returns:
        str: name, converted into a URL- and human-friendly slug.
    """
    return remove_non_word.sub("", name.lower())


def get_show_with_slug(slug: str) -> int:
    """Return the digas ID of the show whose actual slug equals the given slug.

    Args:
        slug (str): The slug the resulting show shall have.

    Returns:
        int: The Digas ID of the show with the given slug.

    Raises:
        NoSuchShowError: If there is no matching show.
    """
    gen = PodcastFeedGenerator(quiet=True)
    shows = gen.show_source.get_show_names
    show_slugs = \
        {
            sluggify(show.name): show
            for name, show in shows.items()
        }
    try:
        return show_slugs[slug].id
    except KeyError as e:
        raise NoSuchShowError from e
