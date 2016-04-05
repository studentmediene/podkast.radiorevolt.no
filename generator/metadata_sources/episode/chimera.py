from .. import SkipEpisode, EpisodeMetadataSource
from ...settings import METADATA_SOURCE
from datetime import datetime
from pytz import timezone
import pytz
import requests
from markdown import Markdown
import urllib.parse
import pdb
from cached_property import cached_property

SETTINGS = METADATA_SOURCE['CHIMERA']


class Chimera(EpisodeMetadataSource):

    def __init__(self):
        EpisodeMetadataSource.__init__(self)
        self._episodes_by_chimera_id = dict()
        self._start_date = SETTINGS['START_DATE']
        self.markdown = Markdown()

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
        return episode.date > self._start_date and episode.sound_url in self._get_episodes(episode.show.show_id)

    def populate(self, episode) -> None:
        try:
            metadata = self._get_episodes(episode.show.show_id)[episode.sound_url]
        except KeyError:
            # episode not in Chimera
            return
        if not metadata['is_published']:
            raise SkipEpisode

        date = datetime.strptime(metadata['public_from'], "%Y-%m-%dT%H:%M:%SZ")
        date = pytz.utc.localize(date)
        episode.date = date

        episode.title = metadata['headline']

        episode.short_description = metadata['lead']

        markdown_description = metadata['body']
        html_description = self.markdown.reset().convert(markdown_description)
        episode.long_description = html_description

        # article URL is not part of the api, so use search page instead
        search_string = urllib.parse.urlencode({"q": metadata['headline']})
        episode.article_url = "http://dusken.no/search/?" + search_string

        episode.image = metadata['image']