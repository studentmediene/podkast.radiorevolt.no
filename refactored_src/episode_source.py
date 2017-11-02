import requests
from .no_episodes_error import NoEpisodesError
from .feed_utils.episode import Episode
import threading
import datetime
from podgen import Media, Person, htmlencode
import pytz

from utils.linkify import linkify


class EpisodeSource:
    """Class for fetching episodes for podcasts.
    """

    def __init__(self, request_session: requests.Session, api_url: str):
        """
        Initialize an episode source.

        Args:
            request_session (requests.Session): The Requests session which will be used when fetching data.
            api_url: Base URL for the REST API.
        """

        self.all_episodes = None
        """List of all episodes, regardless of show, sorted with the most recent first."""

        self.fetch_episode_lock = threading.RLock()
        """Lock ensuring only one thread fetches and parses list of all episodes."""

        self.episodes_by_show = dict()
        """Dictionary with Show ID as key, and a list of episodes as value."""

        self.requests = request_session
        """Requests session to be used when performing requests."""

        self.api_url = api_url
        """Base URL for the Radio Revolt REST API."""

    def _fetch_all_episodes(self) -> list:
        """Fetches a list with all the episodes in the database, regardless of show."""
        episode_list = self.requests.get(
            url=self.api_url + "/lyd/podcast/"
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
            url=self.api_url + "/lyd/podcast/" + str(show_id)
        ).json()
        return episode_list

    def _get_episode_data(self, show):
        """Return list of all episodes for this show, using the all_episodes list if appropriate."""

        # Determine whether all episodes are downloaded in batch or not
        with self.fetch_episode_lock:
            use_all_episodes = self.all_episodes is not None

        if not use_all_episodes:
            # Fetch episodes for this show only
            episodes = self._fetch_episodes_for(show.id)
        else:
            # Use the existing list of episodes and find the relevant ones
            episodes = [episode for episode in self.all_episodes if episode['program_defnr'] == show.id]

        if not episodes:
            raise NoEpisodesError(show.id)
        else:
            return episodes

    def episode_list(self, show):
        """List of Episode objects for the given show."""
        if show.id not in self.episodes_by_show:
            self.episodes_by_show[show.id] = [self.episode(show, episode_dict)
                                                   for episode_dict in self._get_episode_data(show)]
        return self.episodes_by_show[show.id]

    def episode(self, show, episode_dict):
        # Find the publication date
        publication_datetime_str = str(episode_dict['dato']) + " 00:00:00"
        publication_datetime_format = "%Y%m%d %H:%M:%S"
        # Start out with midnight
        publication_date = datetime.datetime.strptime(
            publication_datetime_str,
            publication_datetime_format
        )
        # Then go to the specified time
        publication_datetime_naive = \
            publication_date + datetime.timedelta(seconds=episode_dict['time'])
        # And associate a timezone with that datetime
        timezone = pytz.timezone("Europe/Oslo")
        publication_datetime_aware = \
            timezone.localize(publication_datetime_naive)

        # Create our episode object
        return Episode(
            show=show,
            media=Media(
                episode_dict['url'],
                episode_dict['filesize'],
                None,
                datetime.timedelta(seconds=episode_dict['duration'])
            ),
            id="radiorevolt.no/podkast/episode/" + str(episode_dict['id']),
            deprecated_url=episode_dict['deprecated_url'],
            title=episode_dict['title'],
            summary=linkify(htmlencode(episode_dict['comment']))
                .replace("\n", "<br/>\n"),
            publication_date=publication_datetime_aware,
            authors=[Person(name=episode_dict['author'])] if episode_dict['author'] else [],
        )
