import requests
import json
from .settings import EPISODE_SOURCE as SETTINGS
from . import NoSuchShowError, NoEpisodesError
import threading

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

    def __init__(self, show_id: int):
        """
        Initialize an episode source for the given show.
        :param show_id: DigAS ID for this show.
        """
        self.id = show_id
        """DigAS ID for this show."""

        self.name = None
        """Name of this show."""
        self.exists = False
        """True if the id is known to correspond to a show in the database."""

        self.episodes = None
        """List of episodes for this show, sorted with the most recent first."""

    @staticmethod
    def get_all_shows() -> dict:
        """Returns list of all shows in the database."""
        show_list = requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/programmer/list",
            auth=(SETTINGS['RADIO_REST_API_USERNAME'], SETTINGS['RADIO_REST_API_PASSWORD']),
        ).json()

        # Convert to dictionary with id as key and show name as value (ignoring old)
        return {show['id']: show['name'] for show in show_list}

    @staticmethod
    def get_all_episodes() -> list:
        """Returns a list with all the episodes in the database, regardless of show."""
        episode_list = requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/"
        ).json()
        return episode_list

    @classmethod
    def populate_all_episodes_list(cls):
        """Fetch all podcast episodes. Saves time when processing multiple shows."""
        with cls.fetch_episode_lock:
            if cls.all_episodes is None:
                cls.all_episodes = cls.get_all_episodes()

    @staticmethod
    def get_episodes_for(show_id: int) -> list:
        """Returns a list with all the episodes in the database for the given show."""
        episode_list = requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/" + str(show_id)
        ).json()
        return episode_list

    @classmethod
    def populate_shows(cls):
        cls.shows = cls.get_all_shows()

    def fetch_show_data(self):
        """Populate basic metadata for the show"""
        with self.fetch_show_lock:
            if self.shows is None:
                self.populate_shows()

        # Check if our show_id matches one of the shows
        if self.id in self.shows.keys():
            self.name = self.shows[self.id]
            self.exists = True
        else:
            raise NoSuchShowError(self.id)

    def populate_episodes(self):
        """Populate list of all episodes for this show."""
        if not self.exists:
            self.fetch_show_data()

        with self.fetch_episode_lock:
            use_all_episodes = self.all_episodes is not None

        if not use_all_episodes:
            self.episodes = self.get_episodes_for(self.id)
        else:
            self.episodes = [episode for episode in self.all_episodes if episode['program_defnr'] == self.id]

        if not self.episodes:
            raise NoEpisodesError(self.id)
