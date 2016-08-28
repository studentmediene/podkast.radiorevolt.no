from . import settings as SETTINGS
import logging
from .episode_source import EpisodeSource
from podgen import Podcast, Person, Episode, Category
from .metadata_sources import EpisodeMetadataSource
from .metadata_sources.skip_episode import SkipEpisode
import sys
import traceback


logger = logging.getLogger(__name__)


class Show(Podcast):
    def __init__(
            self,
            name: str,
            id: int,
            **kwargs
    ):
        """Initialize a new show with the provided data.

        Args:
            name (str): Name of the show. Obligatory.
            id (int): DigAS ID for the show. Obligatory.
        """
        self.progress_i = 0
        self.progress_n = None

        super().__init__(**kwargs)
        self.name = name
        self.id = id
        """This Show's Digas ID."""

    def _set_if_false(self, attribute, default_value):
        if not getattr(self, attribute):
            setattr(self, attribute, default_value)

    def _set_if_none(self, attribute, default_value):
        if getattr(self, attribute) is None:
            setattr(self, attribute, default_value)

    def set_defaults(self):
        self._set_if_false("description", SETTINGS.DEFAULT_SHORT_FEED_DESCRIPTION)
        self._set_if_false("category", SETTINGS.DEFAULT_CATEGORY)

        self._set_if_false("language", "no")
        self._set_if_false("website", SETTINGS.DEFAULT_WEBSITE)
        self._set_if_false("authors", SETTINGS.DEFAULT_AUTHORS)
        self._set_if_false("web_master", SETTINGS.DEFAULT_WEBMASTER)
        self._set_if_none("explicit", SETTINGS.DEFAULT_EXPLICIT)
        self._set_if_false("owner", SETTINGS.OWNER)

        if self.owner:
            self._set_if_false("copyright", self.owner.name)

        if not SETTINGS.MARK_OLD_AS_COMPLETE:
            self.complete = False

    def _create_rss(self):
        self.set_defaults()
        return super()._create_rss()

    def add_episodes_to_feed(self, episode_source: EpisodeSource, metadata_sources: list):
        """Add all episodes from the episode_source to this show's feed, populating them with metadata."""
        # Are the metadata sources of the right type?
        for source in metadata_sources:
            assert isinstance(source, EpisodeMetadataSource), "%r is not a subclass of EpisodeMetadataSource." % source
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
            self.add_episode(episode)
        else:
            for episode in episode_source.episode_list(self):
                logger.debug(
                    "Processing episode %(episodename)s (from %(showname)s)",
                    {'episodename': episode.title, 'showname': episode.show.name})
                try:
                    # Let each metadata source provide metadata, if they have it
                    for source in metadata_sources:
                        if source.accepts(episode):
                            source.populate(episode)
                except SkipEpisode as e:
                    # Don't add this episode to the feed
                    logger.info(
                        "Skipping episode named %(name)s (URL: \"%(url)s\")",
                        {"name": episode.title, "url": episode.media.url},
                        exc_info=True
                    )
                    continue
                # Add this episode to the feed
                self.add_episode(episode)
