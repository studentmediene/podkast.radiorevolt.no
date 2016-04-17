from . import metadata_sources
from . import episode_source
from . import Show
from .show_source import ShowSource
from . import NoEpisodesError, NoSuchShowError
from .metadata_sources.skip_show import SkipShow
from . import settings as SETTINGS
from .episode_source import EpisodeSource

from cached_property import cached_property

import sys


class PodcastFeedGenerator:

    def __init__(self, pretty_xml=False, calculate_durations=False, quiet=False):
        self.show_source = ShowSource()
        self.pretty_xml = pretty_xml

        SETTINGS.FIND_EPISODE_DURATIONS = calculate_durations
        SETTINGS.QUIET = quiet

    @cached_property
    def episode_metadata_sources(self):
        # Instantiate them
        return [
            source(
                SETTINGS.METADATA_SOURCE.get(source.__name__, dict()),
                SETTINGS.BYPASS_EPISODE.get(source.__name__, set())
            )
            for source in metadata_sources.EPISODE_METADATA_SOURCES
        ]

    @cached_property
    def show_metadata_sources(self):
        # Instantiate them
        return [
            source(
                SETTINGS.METADATA_SOURCE.get(source.__name__, dict()),
                SETTINGS.BYPASS_SHOW.get(source.__name__, set())
            )
            for source in metadata_sources.SHOW_METADATA_SOURCES
        ]

    def generate_feed(self, show_id: int, force: bool =True) -> bytes:
        """Generate RSS feed for the show represented by the given show_id.

        Args:
            show_id (int): DigAS ID for the show.

        Returns:
            str: The RSS podcast feed for the given show_id.
        """
        try:
            show = self.show_source.shows[show_id]
        except KeyError as e:
            raise NoSuchShowError from e

        return self._generate_feed(show, skip_empty=not force, enable_skip_show=not force)


    def _generate_feed(self, show: Show, skip_empty: bool =True, enable_skip_show: bool =True) -> bytes:
        """Generate RSS feed for the provided show.

        This differs from generate_feed in that it accept Show, not show_id, as argument.

        Args:
            show (Show): The show which shall have its podcast feed generated. Its metadata will be filled by metadata
                sources.

        Returns:
            str: The RSS podcast feed for the given show.
        """

        # Populate show with more metadata
        if not SETTINGS.QUIET:
            print("Finding show metadata...", end="\r", file=sys.stderr)
        self._populate_show_metadata(show, enable_skip_show)

        # Start generating feed
        feed = show.init_feed()

        # Add episodes
        es = episode_source.EpisodeSource(show)
        try:
            es.populate_episodes()
        except NoEpisodesError as e:
            if skip_empty:
                raise e
            else:
                # Go on and generate empty feed
                pass
        show.add_episodes_to_feed(es, self.episode_metadata_sources)

        # Generate!
        return feed.rss_str(pretty=self.pretty_xml)

    def generate_all_feeds_sequence(self) -> dict:
        return self.generate_feeds_sequence(self.show_source.shows.values())

    def generate_feeds_sequence(self, shows) -> dict:
        """Generate RSS feeds for all known shows, one at a time."""
        # Prepare for progress bar
        num_shows = len(shows)
        i = 0

        # Ensure we only download list of episodes once
        if not SETTINGS.QUIET:
            print("Downloading list of episodes", file=sys.stderr)
        EpisodeSource.populate_all_episodes_list()
        if not SETTINGS.QUIET:
            print("Downloading metadata, this could take a while...", file=sys.stderr)
        for source in self.episode_metadata_sources:
            source.prepare_batch()
        for source in self.show_metadata_sources:
            source.prepare_batch()

        feeds = dict()
        for show in shows:
            if not SETTINGS.QUIET:
                # Update progress bar
                i += 1
                print("{0: <60} ({1:03}/{2:03})".format(show.title, i, num_shows),
                      file=sys.stderr)
            try:
                # Do the job
                feeds[show.show_id] = self._generate_feed(show)
            except (NoEpisodesError, SkipShow):
                # Skip this show
                pass

        return feeds

    def get_show_id_by_name(self, name):
        name = name.lower()
        shows = self.show_source.get_show_names
        shows_lower_nospace = {name.lower().replace(" ", ""): show for name, show in shows.items()}
        try:
            return shows_lower_nospace[name].show_id
        except KeyError as e:
            raise NoSuchShowError from e

    def _populate_show_metadata(self, show, enable_skip_show: bool=True):
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
                        pass

