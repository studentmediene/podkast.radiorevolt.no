from .. import ShowMetadataSource
from ...settings import METADATA_SOURCE
from cached_property import cached_property
import json
import os.path
import sys


class ManualChanges(ShowMetadataSource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_key(show):
        return str(show.show_id)

    @cached_property
    def data(self):
        try:
            return json.load(open(os.path.join(os.path.dirname(__file__), "manual_changes.json")))
        except IOError as e:
            print("WARNING: ManualChanges is added as a metadata source for shows, but the configuration file "
                  "generator/metadata_sources/show/manual_changes.json could not be loaded. \nDetails:", e,
                  file=sys.stderr)
            return None
        except ValueError as e:
            print("WARNING: There is an error in generator/metadata_sources/show/manual_changes.json.\nDetails:",
                  e, file=sys.stderr)
            return None

    def accepts(self, show) -> bool:
        try:
            return self._get_key(show) in self.data
        except TypeError:
            return False

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
