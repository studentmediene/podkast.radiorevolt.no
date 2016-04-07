from .. import SkipEpisode, EpisodeMetadataSource
from ...settings import METADATA_SOURCE
from datetime import datetime
from pytz import timezone
import pytz
import requests
from markdown import Markdown
import urllib.parse
from cached_property import cached_property
from sys import stderr

SETTINGS = METADATA_SOURCE['CHIMERA']


class Chimera(EpisodeMetadataSource):
    def __init__(self):
        EpisodeMetadataSource.__init__(self)
        self._episodes_by_chimera_id = dict()
        self._start_date = SETTINGS['START_DATE']
        self._end_date = SETTINGS['END_DATE']
        self._bypass = SETTINGS['BYPASS']
        self.markdown = Markdown(output="html5")
        # Check if the dates are correct
        if self._start_date and self._end_date and self._end_date <= self._start_date:
            print("WARNING: Chimera EpisodeMetadataSource: END_DATE is set _before_ START_DATE in "
                  "generator/settings.py.\n"
                  "This results in this metadata source not matching any episodes.\n"
                  "Please remove Chimera from EPISODE_METADATA_SOURCES in generator/metadata_sources/__init__.py "
                  "if that's what you intended. Otherwise, define a valid range in generator/settings.py for which "
                  "Chimera episode metadata will be used.", file=stderr)


    def _get_episodes(self, digas_id):
        chimera_id = self._shows_by_digas_id[digas_id]
        try:
            return self._episodes_by_chimera_id[chimera_id]
        except KeyError:
            self._episodes_by_chimera_id[chimera_id] = self._fetch_episodes(chimera_id)
            return self._episodes_by_chimera_id[chimera_id]

    @cached_property
    def _shows_by_digas_id(self):
        r = requests.get(SETTINGS['API_URL'] + "/shows/", params={"format": "json"})
        r.raise_for_status()
        shows = r.json()
        return {show['showID']: show['id'] for show in shows}

    @staticmethod
    def _fetch_episodes(chimera_id):
        r = requests.get(
            SETTINGS['API_URL'] + "/episodes/" + str(chimera_id) + "/",
            params={"format": "json"}
        )
        r.raise_for_status()
        episodes = r.json()
        return {episode['podcast_url']: episode for episode in episodes}

    def accepts(self, episode) -> bool:
        """Return True if the episode isn't ignored and is published within the interval in which Chimera is active.

        Start and end date for Chimera is set in settings.py, together with a set with episodes which will be bypassed
        this source."""
        if episode.sound_url in self._bypass:
            return False

        if self._start_date and self._end_date:
            return self._start_date <= episode.date <= self._end_date
        elif self._start_date:
            return self._start_date <= episode.date
        elif self._end_date:
            return episode.date <= self._end_date
        else:
            return True

    def populate(self, episode) -> None:
        try:
            metadata = self._get_episodes(episode.show.show_id)[episode.sound_url]
        except KeyError as e:
            # episode or show not in Chimera - that could mean the article isn't published yet, so hide the episode
            raise SkipEpisode from e
        if not metadata['is_published']:
            raise SkipEpisode

        date = datetime.strptime(metadata['public_from'], "%Y-%m-%dT%H:%M:%SZ")
        date = pytz.utc.localize(date)
        episode.date = date

        episode.title = metadata['headline']

        episode.short_description = metadata['lead']

        # For long_description, use the article lead and body
        markdown_description = """**{0}**\n\n{1}""".format(metadata['lead'], metadata['body'])
        html_description = self.markdown.reset() \
            .convert(markdown_description)
        episode.long_description = html_description

        # article URL is not part of the api, so use search page instead
        search_string = urllib.parse.urlencode({"q": metadata['headline']})
        episode.article_url = "http://dusken.no/search/?" + search_string

        episode.image = metadata['image']
