from .. import SkipEpisode, EpisodeMetadataSource
from datetime import datetime
from pytz import timezone
import pytz
import requests
from markdown import Markdown
import urllib.parse
from cached_property import cached_property
from sys import stderr


class Chimera(EpisodeMetadataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._episodes_by_chimera_id = dict()
        self.markdown = Markdown(output="html5")

    def _get_episodes(self, digas_id):
        chimera_id = self._shows_by_digas_id[digas_id]
        try:
            return self._episodes_by_chimera_id[chimera_id]
        except KeyError:
            self._episodes_by_chimera_id[chimera_id] = self._fetch_episodes(chimera_id)
            return self._episodes_by_chimera_id[chimera_id]

    @cached_property
    def _shows_by_digas_id(self):
        r = requests.get(self.settings['API_URL'] + "/shows/", params={"format": "json"})
        r.raise_for_status()
        shows = r.json()
        return {show['showID']: show['id'] for show in shows}

    def _fetch_episodes(self, chimera_id):
        r = requests.get(
            self.settings['API_URL'] + "/episodes/" + str(chimera_id) + "/",
            params={"format": "json"}
        )
        r.raise_for_status()
        episodes = r.json()
        return {episode['podcast_url']: episode for episode in episodes}

    def accepts(self, episode) -> bool:
        return super().accepts(episode)

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
