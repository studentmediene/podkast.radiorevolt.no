from . import metadata_sources
from . import episode_source
from . import Show
from .show_source import ShowSource
from . import NoEpisodesError, NoSuchShowError
from .metadata_sources.skip_show import SkipShow
from . import settings as SETTINGS

from cached_property import cached_property

import sys


class PodcastFeedGenerator:

    def __init__(self, pretty_xml = False):
        self.show_source = ShowSource()
        self.pretty_xml = pretty_xml

    @cached_property
    def episode_metadata_sources(self):
        # Instantiate them
        return [source() for source in metadata_sources.EPISODE_METADATA_SOURCES]

    @cached_property
    def show_metadata_sources(self):
        # Instantiate them
        return [source() for source in metadata_sources.SHOW_METADATA_SOURCES]

    def generate_feed(self, show_id: int) -> bytes:
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

        return self._generate_feed(show, skip_empty=False, enable_skip_show=False)


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

    def generate_all_feeds_sequence(self) -> list:
        """Generate RSS feeds for all known shows, one at a time."""
        # Prepare for progress bar
        num_shows = len(self.show_source.shows)
        i = 0

        feeds = list()
        for show in self.show_source.shows:
            if not SETTINGS.QUIET:
                # Update progress bar
                i += 1
                print("{0: <30} ({1:03}/{2:03})".format(show.title, i, num_shows),
                      file=sys.stderr)
            try:
                # Do the job
                feeds.append(self._generate_feed(show))
            except (NoEpisodesError, SkipShow):
                # Skip this show
                pass

        return feeds

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

