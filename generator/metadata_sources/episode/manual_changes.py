from .. import EpisodeMetadataSource
from ..base_manual_changes import BaseManualChanges
from cached_property import cached_property
import json
import os.path
import sys
from datetime import datetime


class ManualChanges(BaseManualChanges, EpisodeMetadataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def _is_episode_source(self):
        return True

    @cached_property
    def _config_file_settings_key(self):
        return "EPISODE_CONFIG"

    def accepts(self, episode) -> bool:
        return super().accepts(episode)

    @staticmethod
    def _get_key(episode):
        return str(episode.sound_url)

    def populate(self, episode) -> None:
        metadata = self.data[self._get_key(episode)]

        episode.title = metadata.get("title", episode.title)
        if "date" in metadata:
            try:
                episode.date = datetime.strptime(metadata['date'], "%Y-%m-%d %H:%M:%S %z")
            except ValueError:
                print("WARNING: Date {date} in file {file} could not be parsed, so it was ignored.\n"
                      "Make sure it's on the following form (±HHMM being timezone offset):\n"
                      "    YYYY-MM-DD HH:MM:SS ±HHMM".format(date=metadata['date'], file=self._config_file),
                      file=sys.stderr)
        episode.short_description = metadata.get("short_description", episode.short_description)
        episode.long_description = metadata.get("long_description", episode.long_description)
        episode.image = metadata.get("image", episode.image)
        episode.author = metadata.get("author", episode.author)
        episode.author_email = metadata.get("author_email", episode.author_email)
        episode.explicit = metadata.get("explicit", episode.explicit)
        episode.article_url = metadata.get("article_url", episode.article_url)

        recognized_keys = {"title", "date", "short_description", "long_description", "image", "author",
                           "author_email", "explicit", "article_url"}
        self.check_for_unrecognized_keys(metadata, recognized_keys, self._get_key(episode))
