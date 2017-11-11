import datetime

import warnings
import requests
import requests.auth
from .feed_utils.show import Show
from cached_property import threaded_cached_property as cached_property


class ShowSource:
    """Class for fetching shows and information about them"""

    def __init__(self, request_session: requests.Session, api_url, username, password):
        """
        Use the given requests session when fetching data.

        Args:
            request_session: Request object to use to make requests.
            api_url: Base URL for Radio REST API.
            username
            """
        self.requests = request_session
        self.api_url = api_url
        self.username = username
        self.password = password
        self.last_fetched = None

    def invalidate(self):
        if self.raw_shows:
            del self.raw_shows
        if self.show_names:
            del self.show_names

    @cached_property
    def raw_shows(self):
        self.last_fetched = datetime.datetime.now(datetime.timezone.utc)
        return {show_dict['id']: show_dict for show_dict in self._fetch_all_shows()}

    def get_show(self, digas_id: int) -> Show:
        """
        Fetch the show with the given Digas ID, raise KeyError when not found.
        """
        show = self.raw_shows[digas_id]
        return Show(name=show['name'], id=show['id'])

    def get_all_shows(self):
        all_shows = []
        for show in self.raw_shows.values():
            digas_id = show['id']
            all_shows.append(self.get_show(digas_id))
        return all_shows

    @property
    def shows(self):
        """dict: Dictionary with all shows, with their DigAS ID as key and Show instance as value."""
        warnings.warn("ShowSource.shows is deprecated, ShowSource.get_show should be used instead.", DeprecationWarning, stacklevel=2)
        return self._get_all_shows()

    def _fetch_all_shows(self):
        r = self.requests.get(
            url=self.api_url + "/programmer/list",
            auth=requests.auth.HTTPDigestAuth(self.username, self.password),
        )
        r.raise_for_status()
        r.encoding = "ISO 8859-1"
        show_list = r.json()
        return show_list

    def _get_all_shows(self) -> dict:
        """Returns list of all shows in the database."""
        # Convert to dictionary with id as key
        return {show['id']: Show(name=show['name'], id=show['id']) for show in self.raw_shows.values()}

    @property
    def get_show_names(self) -> dict:
        """Get dictionary with show.name as key and show as value.

        Useful when searching for a show by its name."""
        warnings.warn("ShowSource.get_show_names is deprecated, ShowSource.show_names should be used instead.", DeprecationWarning, stacklevel=2)
        return {show.name: show for show in self._get_all_shows().values()}

    @cached_property
    def show_names(self) -> dict:
        """Get dictionary with each show's name as key and Digas ID as value."""
        return {show['name']: show['id'] for show in self.raw_shows.values()}
