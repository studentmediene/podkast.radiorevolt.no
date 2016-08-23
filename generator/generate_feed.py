import logging
import threading

import copy
from .metadata_sources.skip_episode import SkipEpisode
from . import metadata_sources, set_up_logger
from .episode_source import EpisodeSource
from . import Show
from .show_source import ShowSource
from . import NoEpisodesError, NoSuchShowError
from .metadata_sources.skip_show import SkipShow
from . import settings as SETTINGS
import requests

from cached_property import threaded_cached_property as cached_property
from clint.textui import progress

import sys
import re
import datetime


logger = logging.getLogger(__name__)


class PodcastFeedGenerator:

    def __init__(self, pretty_xml=False, quiet=False, xslt=None):
        self.requests = requests.Session()
        self.requests.headers.update({"User-Agent": "podcast-feed-gen"})

        self.show_source = ShowSource(self.requests)
        self.episode_source = EpisodeSource(self.requests)
        self.pretty_xml = pretty_xml
        self.re_remove_chars = re.compile(r"[^\w\d]|_")

        self.created = datetime.datetime.utcnow()

        self.xslt = xslt

        self.quiet = quiet
        self.hide_progressbar = True if quiet else None
        if quiet:
            set_up_logger.quiet()
        self.has_prepared_for_batch = False
        self.prepare_batch_lock = threading.RLock()

    @staticmethod
    def register_redirect_services(sound_redirect, article_redirect):
        SETTINGS.URL_REDIRECTION_SOUND_URL = sound_redirect
        SETTINGS.URL_REDIRECTION_ARTICLE_URL = article_redirect

    @cached_property
    def episode_metadata_sources(self):
        # Instantiate them
        return [
            source(
                SETTINGS.METADATA_SOURCE.get(source.__name__, dict()),
                SETTINGS.BYPASS_EPISODE.get(source.__name__, set()),
                self.requests
            )
            for source in metadata_sources.EPISODE_METADATA_SOURCES
        ]

    @cached_property
    def show_metadata_sources(self):
        # Instantiate them
        return [
            source(
                SETTINGS.METADATA_SOURCE.get(source.__name__, dict()),
                SETTINGS.BYPASS_SHOW.get(source.__name__, set()),
                self.requests
            )
            for source in metadata_sources.SHOW_METADATA_SOURCES
        ]

    def generate_feed(self, show_id: int, force: bool =True) -> bytes:
        """Generate RSS feed for the show represented by the given show_id.

        Args:
            show_id (int): DigAS ID for the show.
            force (bool): Set to False to throw NoEpisodesError if there are no episodes for the given show.
                Set to True to just generate the feed with no episodes in such cases.

        Returns:
            str: The RSS podcast feed for the given show_id.
        """
        try:
            show = copy.deepcopy(self.show_source.shows[show_id])
        except KeyError as e:
            raise NoSuchShowError from e

        return self._generate_feed(show, skip_empty=not force,
                                   enable_skip_show=not force)

    def _generate_feed(self, show: Show, skip_empty: bool = True,
                       enable_skip_show: bool = True) -> bytes:
        """Generate RSS feed for the provided show.

        This differs from generate_feed in that it accept Show, not show_id, as argument.

        Args:
            show (Show): The show which shall have its podcast feed generated. Its metadata will be filled by metadata
                sources.
            skip_empty (bool): Set to true to raise exception if there are no episodes for this show.
            enable_skip_show (bool): Skip this show if any Show Metadata source raises SkipShow.

        Returns:
            str: The RSS podcast feed for the given show.
        """

        # Populate show with more metadata
        logger.info("Finding show metadata...")
        self.populate_show_metadata(show, enable_skip_show)
        show.xslt = self.xslt

        # Add episodes
        try:
            self.episode_source.episode_list(show)
        except NoEpisodesError as e:
            if skip_empty:
                raise e
            else:
                # Go on and generate empty feed
                pass
        show.add_episodes_to_feed(self.episode_source, self.episode_metadata_sources)

        # Generate!
        return show.rss_str(minimize=not self.pretty_xml)

    def generate_all_feeds_sequence(self) -> dict:
        return self.generate_feeds_sequence(self.show_source.shows.values())

    def generate_feeds_sequence(self, shows) -> dict:
        """Generate RSS feeds for all known shows, one at a time."""
        # Prepare for progress bar
        num_shows = len(shows)
        i = 0

        logger.info("Generating %s feeds in batch", num_shows)

        # Ensure we only download list of episodes once
        logger.info("Downloading metadata, this could take a while...")
        self.prepare_for_batch()

        feeds = dict()
        for show in progress.bar(shows, hide=self.hide_progressbar):
            # Also log progress
            i += 1
            logger.debug("{0: <60} ({1:03}/{2:03})".format(show.name, i, num_shows))
            try:
                # Do the job
                feeds[show.id] = self._generate_feed(show)
            except (NoEpisodesError, SkipShow):
                # Skip this show
                pass

        logger.info("Done creating the feeds.")
        return feeds

    def prepare_for_batch(self):
        with self.prepare_batch_lock:
            if self.has_prepared_for_batch:
                return
            logger.debug("Preparing for processing multiple shows")
            self.episode_source.populate_all_episodes_list()
            for source in self.episode_metadata_sources:
                source.prepare_batch()
            for source in self.show_metadata_sources:
                source.prepare_batch()
            self.has_prepared_for_batch = True
            return

    def get_show_id_by_name(self, name):
        name = name.lower()
        shows = self.show_source.get_show_names
        shows_lower_nospace = {self.re_remove_chars.sub("", name.lower()): show for name, show in shows.items()}
        try:
            return shows_lower_nospace[name].id
        except KeyError as e:
            raise NoSuchShowError from e

    def populate_show_metadata(self, show, enable_skip_show: bool=True):
        for source in self.show_metadata_sources:
            if source.accepts(show):
                try:
                    source.populate(show)
                except SkipShow as e:
                    if enable_skip_show:
                        # Skip
                        raise e
                    else:
                        # We're not skipping this show, just go on...
                        logger.debug("Ignoring SkipShow", exc_info=True)

    def get_empty_all_episodes_show(self):
        return Show(id=0, **SETTINGS.ALL_EPISODES_FEED_METADATA)

    def generate_feed_with_all_episodes(self):
        show = self.get_empty_all_episodes_show()
        show.xslt = self.xslt
        self.prepare_for_batch()
        # Get all episodes
        episodes = [self.episode_source.episode(self.show_source.shows[ep['program_defnr']], ep)
                    for ep in self.episode_source.all_episodes if ep['program_defnr'] != 0]
        # Populate metadata
        for episode in progress.bar(episodes, hide=self.hide_progressbar):
            logger.debug("Populating episode %s (from %s)", episode.title,
                         episode.show.name)
            try:
                for source in self.episode_metadata_sources:
                    if source.accepts(episode):
                        source.populate(episode)
            except SkipEpisode:
                logger.info(
                    "Skipping episode named %(name)s (URL: \"%(url)s\")",
                    {"name": episode.title, "url": episode.media.url},
                    exc_info=True
                )
                continue
            show.add_episode(episode)

        return show.rss_str(minimize=not self.pretty_xml)
