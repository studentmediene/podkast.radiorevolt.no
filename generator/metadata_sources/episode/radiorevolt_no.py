import logging
from .. import EpisodeMetadataSource
from datetime import datetime
import pytz
import rfc3339
import json
from cached_property import threaded_cached_property as cached_property


class RadioRevolt_no(EpisodeMetadataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def _metadata_by_sound_url(self):
        data = self._fetch_episodes()
        episodes = dict()
        for episode in data:
            podcast_url = episode['podcastUrl']
            # Skip all episodes with no associated podcast URL
            if podcast_url:
                episodes[podcast_url] = episode
        return episodes

    def _fetch_episodes(self):
        r = self.requests.get(
            self.settings['API_URL'] + "/episodes",
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
        # Slug is not supported yet
        # link = self.settings['EPISODE_WEBSITE_TEMPLATE'] % metadata['slug']

        episode.title = title
        if not episode.summary:
            episode.summary = lead
        episode.publication_date = max(date, episode.publication_date)
        # episode.link = link
