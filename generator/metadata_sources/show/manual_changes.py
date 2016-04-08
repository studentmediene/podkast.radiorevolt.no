from .. import ShowMetadataSource
from ..base_manual_changes import BaseManualChanges
from ...settings import METADATA_SOURCE
from cached_property import cached_property
import json
import os.path
import sys


class ManualChanges(BaseManualChanges, ShowMetadataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def _is_episode_source(self):
        return False

    @cached_property
    def _config_file_settings_key(self):
        return "SHOW_CONFIG"

    @staticmethod
    def _get_key(show):
        return str(show.show_id)

    def accepts(self, show) -> bool:
        return super().accepts(show)

    def populate(self, show) -> None:
        metadata = self.data[self._get_key(show)]

        show.title = metadata.get("title", show.title)

        show.short_description = metadata.get("short_description", show.short_description)
        show.long_description = metadata.get("long_description", show.long_description)
        show.category = metadata.get("category", show.category)
        show.sub_category = metadata.get("sub_category", show.sub_category)
        show.image = metadata.get("image", show.image)
        show.author = metadata.get("author", show.author)
        show.editorial_email = metadata.get("editorial_email", show.editorial_email)
        show.technical_email = metadata.get("technical_email", show.technical_email)
        show.old = metadata.get("old", show.old)
        show.explicit = metadata.get("explicit", show.explicit)
        show.show_url = metadata.get("show_url", show.show_url)
        show.language = metadata.get("language", show.language)
        show.copyright = metadata.get("copyright", show.copyright)

        recognized_keys = {"title", "short_description", "long_description", "category", "sub_category", "image",
                           "author", "editorial_email", "technical_email", "old", "explicit", "show_url",
                           "language", "copyright"}
        self.check_for_unrecognized_keys(metadata, recognized_keys, self._get_key(show))
