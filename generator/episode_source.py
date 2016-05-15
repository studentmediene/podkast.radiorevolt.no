import requests
from .settings import EPISODE_SOURCE as SETTINGS
from .no_episodes_error import NoEpisodesError
from .episode import Episode
import threading
import datetime
import time


class EpisodeSource:
    """Class for fetching episodes for podcasts.
    """

    def __init__(self, request_session: requests.Session):
        """
        Initialize an episode source.

        Args:
            request_session (requests.Session): The Requests session which will be used when fetching data.
        """

        self.all_episodes = None
        """List of all episodes, regardless of show, sorted with the most recent first."""

        self.fetch_episode_lock = threading.RLock()
        """Lock ensuring only one thread fetches and parses list of all episodes."""

        self.episodes_by_show = dict()
        """Dictionary with Show ID as key, and a list of episodes as value."""

        self.requests = request_session
        """Requests session to be used when performing requests."""

    def _fetch_all_episodes(self) -> list:
        """Fetches a list with all the episodes in the database, regardless of show."""
        episode_list = self.requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/"
        ).json()
        return episode_list

    def populate_all_episodes_list(self):
        """Fetch all podcast episodes. Saves time when processing multiple shows."""
        with self.fetch_episode_lock:
            if self.all_episodes is None:
                self.all_episodes = self._fetch_all_episodes()

    def _fetch_episodes_for(self, show_id: int) -> list:
        """Returns a list with all the episodes in the database for the given show ID."""
        episode_list = self.requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/lyd/podcast/" + str(show_id)
        ).json()
        return episode_list

    def _get_episode_data(self, show):
        """Return list of all episodes for this show, using the all_episodes list if appropriate."""

        # Determine whether all episodes are downloaded in batch or not
        with self.fetch_episode_lock:
            use_all_episodes = self.all_episodes is not None

        if not use_all_episodes:
            # Fetch episodes for this show only
            episodes = self._fetch_episodes_for(show.show_id)
        else:
            # Use the existing list of episodes and find the relevant ones
            episodes = [episode for episode in self.all_episodes if episode['program_defnr'] == show.show_id]

        if not episodes:
            raise NoEpisodesError(show.show_id)
        else:
            return episodes

    def episode_list(self, show):
        """List of Episode objects for the given show."""
        if show.show_id not in self.episodes_by_show:
            try:
                self.episodes_by_show[show.show_id] = [self.episode(show, episode_dict, self.requests)
                                                       for episode_dict in self._get_episode_data(show)]
            except NoEpisodesError as e:
                self.episodes_by_show[show.show_id] = []
                raise e
        return self.episodes_by_show[show.show_id]

    @staticmethod
    def episode(show, episode_dict, requests_session):
        return Episode(
            show=show,
            sound_url=episode_dict['url'],
            title=episode_dict['title'],
            long_description=episode_dict['comment'],
            date=datetime.datetime.strptime(str(episode_dict['dato']) + " 12:00:00 " + time.strftime("%z"),
                                            "%Y%m%d %H:%M:%S %z"),
            author=episode_dict['author'],
            requests_session=requests_session
        )
