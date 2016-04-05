import requests
from .settings import EPISODE_SOURCE as SETTINGS
from .no_episodes_error import NoEpisodesError
from .episode import Episode
import threading
import datetime
import time
from cached_property import cached_property

class EpisodeSource:
    """Class for fetching episodes for a podcast.
    """
    shows = None
    """Dictionary containing all known shows."""
    all_episodes = None
    """List of all episodes, regardless of show, sorted with the most recent first."""

    fetch_show_lock = threading.RLock()
    """Lock ensuring only one thread fetches and parses list of shows."""
    fetch_episode_lock = threading.RLock()
    """Lock ensuring only one thread fetches and parses list of all episodes."""

    def __init__(self, show):
        """
        Initialize an episode source for the given show.

        :param show: Fetch episodes for this show.
        """
        self.id = show.show_id
        """DigAS ID for this show."""

        self.show = show

        self.episodes = None
        """List of episodes for this show, sorted with the most recent first."""


    @staticmethod
    def _get_all_episodes() -> list:
        """Fetches a list with all the episodes in the database, regardless of show."""
        episode_list = requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/"
        ).json()
        return episode_list

    @classmethod
    def populate_all_episodes_list(cls):
        """Fetch all podcast episodes. Saves time when processing multiple shows."""
        with cls.fetch_episode_lock:
            if cls.all_episodes is None:
                cls.all_episodes = cls._get_all_episodes()

    @staticmethod
    def _get_episodes_for(show_id: int) -> list:
        """Returns a list with all the episodes in the database for the given show."""
        episode_list = requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/" + str(show_id)
        ).json()
        return episode_list

    def populate_episodes(self):
        """Populate list of all episodes for this show."""

        # Determine whether all episodes are downloaded in batch or not
        with self.fetch_episode_lock:
            use_all_episodes = self.all_episodes is not None

        if not use_all_episodes:
            # Fetch episodes for this show only
            self.episodes = self._get_episodes_for(self.id)
        else:
            # Use the existing list of episodes and find the relevant ones
            self.episodes = [episode for episode in self.all_episodes if episode['program_defnr'] == self.id]

        if not self.episodes:
            raise NoEpisodesError(self.id)

    @cached_property
    def episode_list(self):
        """List of Episode objects."""
        return [
            Episode(
                show=self.show,
                sound_url=episode_dict['url'],
                title=episode_dict['title'],
                long_description=episode_dict['comment'],
                date=datetime.datetime.strptime(str(episode_dict['dato']) + " 12:00:00 " + time.strftime("%z"),
                                                "%Y%m%d %H:%M:%S %z"),
                author=episode_dict['author'],
            ) for episode_dict in self.episodes]
