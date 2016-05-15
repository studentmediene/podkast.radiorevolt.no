from . import settings as SETTINGS
from .episode_source import EpisodeSource
from feedgen.feed import FeedGenerator
from .metadata_sources import EpisodeMetadataSource
from .metadata_sources.skip_episode import SkipEpisode
import sys
import traceback


class Show:
    def __init__(
            self,
            title: str,
            show_id: int,
            short_description: str =None,
            image: str =None,
            category: str =None,
            sub_category: str =None,
            language: str ="no",
            show_url: str =None,
            editorial_email: str =None,
            technical_email: str =None,
            copyright_: str =None,
            old: bool =False,
            long_description: str =None,
            author: str =None,
            explicit: bool =None,
            owner_name: str =None,
            owner_email: str =None
    ):
        """Initialize a new show with the provided data.

        Args:
            title (str): Name of the show. Obligatory.
            show_id (int): DigAS ID for the show. Obligatory.
            short_description (str): Short description (couple words) describing the show.
                Defaults to something generic.
            image (str): URL for image which will be used for this show. It must be PNG or JPEG, and it must
                be between 1400x1400 and 3000x3000 in resolution. Change the URL if the image changes. Defaults to no
                image.
            category (str): iTunes category for this show. See
                https://help.apple.com/itc/podcasts_connect/#/itc9267a2f12 for available categories. Defaults to value
                in settings.py.
            sub_category (str): iTunes sub-category for this show. See
                https://help.apple.com/itc/podcasts_connect/#/itc9267a2f12 for available sub-categories. Defaults to
                value in settings.py.
            language (str): Language of this show. Use one of the two-letter values found in
                http://www.loc.gov/standards/iso639-2/php/code_list.php. Default value is in settings.py.
            show_url (str): This show's website. Defaults to whatever default is in settings.py.
            editorial_email (str): Email for whoever is responsible for the content. Default value is in settings.py.
            technical_email (str): Email for whoever is responsible for the technical aspect of the feed, for instance
                the webmaster. Default value is in settings.py.
            copyright_ (str): Information about this show's copyright. Defaults to nothing.
            old (bool): Set to True if there won't be published more podcast episodes for this feed.
            long_description (str): Long description, which is used when you hover the i icon in iTunes. Defaults to
                short_description.
            author (str): Name of the author. Defaults to the title (that is, the show name).
            explicit (bool): True if this show is inappropriate for children,
                False it it's appropriate, None to use the default value from settings.py.
            owner_name (str): Name of the owner, which will be contacted by iTunes in case of problems. Defaults to
                value in settings.py.
            owner_email (str): Email of the owner, which will be contacted by iTunes in case of problems. Defaults to
                value in settings.py.
        """
        self.title = title
        """str: Name of the show."""
        self.show_id = show_id
        """int: DigAS ID for the show."""

        self.short_description = short_description or SETTINGS.DEFAULT_SHORT_FEED_DESCRIPTION
        """str: Short description (couple words) describing the show."""
        self.long_description = long_description or self.short_description
        """str: Long description, which is used when you hover the i icon in iTunes."""
        self.image = image
        """str: URL for image which will be used for this show. It must be PNG or JPEG, and it must
    be between 1400x1400 and 3000x3000 in resolution. Change the URL if the image changes."""

        self._category = None
        """str: iTunes category for this show."""

        self.category = category or SETTINGS.DEFAULT_CATEGORY

        if category:
            # Use the default None value if just the main category was supplied
            # (but use the supplied value if it's there)
            actual_sub_category = sub_category
        else:
            if sub_category:
                raise ValueError("You cannot define just a sub-category; you'll either need to specify both category"
                    " and sub-category or just the main category.")
            else:
                actual_sub_category = SETTINGS.DEFAULT_SUB_CATEGORY
        # Do the assignment outside of the conditionals, so we don't screw up the docstring
        self.sub_category = actual_sub_category
        """str: iTunes sub-category for this show. See
    https://help.apple.com/itc/podcasts_connect/#/itc9267a2f12 for available sub-categories."""

        self.language = language
        """str: Language of this show. Use one of the two-letter values found in
    http://www.loc.gov/standards/iso639-2/php/code_list.php."""
        self.show_url = show_url or SETTINGS.DEFAULT_WEBSITE
        """str: This show's website."""
        self.editorial_email = editorial_email or SETTINGS.DEFAULT_EDITORIAL_EMAIL
        """str: Email for whoever is responsible for the content."""
        self.technical_email = technical_email or SETTINGS.DEFAULT_TECHNICAL_EMAIL
        """str: Email for whoever is responsible for the technical aspect of the feed, for instance the webmaster."""
        self.copyright = copyright_
        """str: Information about this show's copyright."""
        self.old = old
        """bool: Set to True if there won't be published more podcast episodes for this feed."""
        self.author = author or title
        """str: Name of the author/artist."""
        self.explicit = explicit if explicit is not None else SETTINGS.DEFAULT_EXPLICIT
        """bool: True if this show is explicit, False if this show is clean."""
        self.owner_name = owner_name or SETTINGS.OWNER_NAME
        """str: Name of the owner, which will be contacted by iTunes in case of problems."""
        self.owner_email = owner_email or SETTINGS.OWNER_EMAIL
        """str: Email of the owner, which will be contacted by iTunes in case of problems."""

        self.feed = None
        """FeedGenerator: Reference to the FeedGenerator associated with this show."""

        self.progress_i = 0
        self.progress_n = None

    @property
    def category(self):
        """str: iTunes category for this show. See
    https://help.apple.com/itc/podcasts_connect/#/itc9267a2f12 for available categories.
    Note that changing the category will automatically set sub_category to None."""
        return self._category

    @category.setter
    def category(self, new_category):
        # sub_category is invalid if the category is changed, so make it None
        # Thus, if you set category to something, you'll need to set sub_category _after_ setting category.
        if new_category != self.category:
            self.sub_category = None
        self._category = new_category

    def init_feed(self) -> FeedGenerator:
        feed = FeedGenerator()
        feed.load_extension('podcast', rss=True)

        feed.title(self.title)

        feed.podcast.itunes_subtitle(self.short_description)
        feed.description(self.short_description)
        feed.podcast.itunes_summary(self.long_description)
        if self.image is not None:
            feed.podcast.itunes_image(self.image)

        if self.category is not None:
            if self.sub_category is not None:
                feed.podcast.itunes_category(self.category, self.sub_category)
            else:
                feed.podcast.itunes_category(self.category)

        feed.language(self.language)
        feed.link({'href': self.show_url})
        feed.managingEditor(self.editorial_email)
        feed.webMaster(self.technical_email)

        if self.copyright is not None:
            feed.rights(self.copyright)

        if SETTINGS.MARK_OLD_AS_COMPLETE:
            feed.podcast.itunes_complete(self.old)
        else:
            feed.podcast.itunes_complete(False)

        feed.podcast.itunes_author(self.author)
        feed.podcast.itunes_explicit("yes" if self.explicit else "no")
        feed.podcast.itunes_owner(name=self.owner_name, email=self.owner_email)

        self.feed = feed

        return feed

    def add_episodes_to_feed(self, episode_source: EpisodeSource, metadata_sources: list):
        """Add all episodes from the episode_source to this show's feed, populating them with metadata."""
        # Are the metadata sources of the right type?
        for source in metadata_sources:
            assert isinstance(source, EpisodeMetadataSource), "%r is not a subclass of EpisodeMetadataSource." % source
        if not SETTINGS.QUIET:
            print("Processing episodes...            ", file=sys.stderr, end="\r")
        self.progress_n = len(episode_source.episode_list(self))
        if self.progress_n == 1:
            # add the single episode, but ignore SkipEpisode
            episode = episode_source.episode_list(self)[0]
            for source in metadata_sources:
                if source.accepts(episode):
                    try:
                        source.populate(episode)
                    except SkipEpisode:
                        pass
            episode.add_to_feed(self.feed)
            episode.populate_feed_entry()
            self._progress_increment()
        else:
            for episode in episode_source.episode_list(self):
                try:
                    # Let each metadata source provide metadata, if they have it
                    for source in metadata_sources:
                        if source.accepts(episode):
                            source.populate(episode)
                except SkipEpisode as e:
                    # Don't add this episode to the feed
                    if not SETTINGS.QUIET:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        cause = traceback.extract_tb(exc_traceback, 2)[1][0]
                        print("NOTE: Skipping episode named {name}\n    URL: \"{url}\"\n    Caused by {cause}\n"
                              .format(name=episode.title, url=episode.sound_url, cause=cause),
                              file=sys.stderr)

                    self._progress_increment()
                    continue
                # Add this episode to the feed
                episode.add_to_feed(self.feed)
                episode.populate_feed_entry()
                self._progress_increment()

    def _progress_increment(self):
        if not SETTINGS.QUIET:
            self.progress_i += 1
            print(
                "Processed episode {0} of {1}                    ".format(self.progress_i, self.progress_n),
                file=sys.stderr, end="\r"
            )
