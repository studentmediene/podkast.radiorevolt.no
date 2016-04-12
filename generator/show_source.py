import requests
import requests.auth
from .settings import SHOW_SOURCE as SETTINGS
from .show import Show
from cached_property import cached_property


class ShowSource:
    """Class for fetching shows and information about them"""

    @cached_property
    def shows(self):
        """dict: Dictionary with all shows, with their DigAS ID as key and Show instance as value."""
        return self._get_all_shows()

    @staticmethod
    def _get_all_shows() -> dict:
        """Returns list of all shows in the database."""
        r = requests.get(
            url=SETTINGS['RADIO_REST_API_URL'] + "/programmer/list",
            auth=requests.auth.HTTPDigestAuth(SETTINGS['RADIO_REST_API_USERNAME'], SETTINGS['RADIO_REST_API_PASSWORD']),
        )
        r.raise_for_status()
        r.encoding = "ISO 8859-1"
        show_list = r.json()

        # Convert to dictionary with id as key
        return {show['id']: Show(title=show['name'], show_id=show['id']) for show in show_list}

    @cached_property
    def get_show_names(self) -> dict:
        """Get dictionary with show_id as key and show name as value.

        Useful when searching for a show by its name."""
        return {show.title: show for show in self.shows}
