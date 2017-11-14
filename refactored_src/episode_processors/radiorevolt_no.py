import rfc3339
from cached_property import threaded_cached_property as cached_property

from episode_processors import EpisodeProcessor


class RadioRevolt_no(EpisodeProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def _metadata_by_sound_url(self):
        data = self._fetch_episodes()
        episode_list = data['data']['allEpisodes']
        return {episode['podcastUrl']: episode for episode in episode_list if
                episode['podcastUrl']}

    def _fetch_episodes(self):
        r = self.requests.get(
            self.settings['API_URL'],
            params={"query": """
            {
              allEpisodes {
                podcastUrl,
                title,
                lead,
                createdAt,
              }
            }
            """},
        )
        r.raise_for_status()
        return r.json()

    def accepts(self, episode) -> bool:
        return super().accepts(episode) and \
               episode.media.url in self._metadata_by_sound_url

    def populate(self, episode) -> None:
        metadata = self._metadata_by_sound_url[episode.media.url]

        title = metadata['title']
        lead = metadata['lead']
        date = rfc3339.parse_datetime(metadata['createdAt'])

        episode.title = title
        episode.summary = lead
        episode.publication_date = max(date, episode.publication_date)
