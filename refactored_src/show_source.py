import datetime

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

    @cached_property
    def shows(self):
        """dict: Dictionary with all shows, with their DigAS ID as key and Show instance as value."""
        self.last_fetched = datetime.datetime.now(datetime.timezone.utc)
        return self._get_all_shows()

    def _get_all_shows(self) -> dict:
        """Returns list of all shows in the database."""
        r = self.requests.get(
            url=self.api_url + "/programmer/list",
            auth=requests.auth.HTTPDigestAuth(self.username, self.password),
        )
        r.raise_for_status()
        r.encoding = "ISO 8859-1"
        show_list = r.json()

        # Convert to dictionary with id as key
        return {show['id']: Show(name=show['name'], id=show['id']) for show in show_list}

    @cached_property
    def get_show_names(self) -> dict:
        """Get dictionary with show.name as key and show as value.

        Useful when searching for a show by its name."""
        return {show.name: show for show in self.shows.values()}
