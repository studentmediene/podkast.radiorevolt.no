import logging
from threading import RLock
from datetime import datetime

import pytz
from markdown import Markdown
from cached_property import threaded_cached_property as cached_property

from episode_processors import SkipEpisode, EpisodeProcessor


logger = logging.getLogger(__name__)


class Chimera(EpisodeProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._episodes_by_chimera_id = dict()
        self.markdown = Markdown(output="html5")
        self._episode_list_locks = dict()

    def _get_episodes(self, digas_id):
        try:
            chimera_id = self._shows_by_digas_id[digas_id]
        except KeyError:
            # Digas ID not recognized
            return []
        with self._episode_list_locks.setdefault(chimera_id, RLock()):
            try:
                return self._episodes_by_chimera_id[chimera_id]
            except KeyError:
                self._episodes_by_chimera_id[chimera_id] = self._fetch_episodes(chimera_id)
                return self._episodes_by_chimera_id[chimera_id]

    @cached_property
    def _shows_by_digas_id(self):
        r = self.requests.get(self.settings['api'] + "/shows/", params={"format": "json"})
        r.raise_for_status()
        shows = r.json()
        return {show['showID']: show['id'] for show in shows}

    def _fetch_episodes(self, chimera_id):
        r = self.requests.get(
            self.settings['api'] + "/episodes/" + str(chimera_id) + "/",
            params={"format": "json"}
        )
        r.raise_for_status()
        episodes = r.json()
        return {episode['podcast_url']: episode for episode in episodes}

    def accepts(self, episode) -> bool:
        return super().accepts(episode) and episode.deprecated_url in self._get_episodes(episode.show.id)

    def populate(self, episode) -> None:
        metadata = self._get_episodes(episode.show.id)[episode.deprecated_url]
        if not metadata['is_published']:
            raise SkipEpisode

        try:
            date = datetime.strptime(metadata['public_from'], "%Y-%m-%dT%H:%M:%SZ")
            date = pytz.utc.localize(date)
            episode.publication_date = date
        except ValueError:
            # published date can be ill-formed
            logger.info("Couldn't parse date %s", metadata['public_from'],
                        exc_info=True)
            pass

        episode.title = metadata['headline']

        episode.summary = metadata['lead']

        # For long_description, use the article lead and body
        markdown_description = """**{0}**\n\n{1}""".format(metadata['lead'], metadata['body'])
        html_description = self.markdown.reset() \
            .convert(markdown_description)
        episode.long_summary = html_description

        # Do not add link
        # article URL is not part of the api, so use search page instead
        # search_string = urllib.parse.urlencode({"q": metadata['headline']})
        # episode.link = "http://dusken.no/search/?" + search_string

        episode.image = metadata['image']
