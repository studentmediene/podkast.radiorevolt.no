from time import strptime

from .. import ShowMetadataSource
from ..base_manual_changes import BaseManualChanges
from ...settings import METADATA_SOURCE
from cached_property import cached_property
import json
import os.path
import sys
from podgen import Person, Category


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
        return str(show.id)

    def accepts(self, show) -> bool:
        return super().accepts(show)

    def populate(self, show) -> None:
        metadata = self.data[self._get_key(show)]

        for attribute, value in metadata.items():
            if hasattr(show, attribute):
                if attribute in ("publication_date", "last_updated"):
                    try:
                        setattr(show, attribute, strptime(value, "%Y-%m-%d %H:%M:%S %z"))
                    except ValueError:
                        print("WARNING: Date {date} in file {file} could not be parsed, so it was ignored.\n"
                              "Make sure it's on the following form (±HHMM being timezone offset):\n"
                              "    YYYY-MM-DD HH:MM:SS ±HHMM".format(date=metadata['date'], file=self._config_file),
                              file=sys.stderr)
                elif attribute == "authors":
                    authors = [Person(p.get('name'), p.get('email')) for p in value]
                    show.authors = authors
                elif attribute == "web_master":
                    show.web_master = Person(value.get('name'), value.get('email'))
                elif attribute == "category":
                    if len(value) == 2:
                        show.category = Category(value[0], value[1])
                    else:
                        show.category = Category(value[0])
                else:
                    setattr(show, attribute, value)
            else:
                print("WARNING {source}: Attribute {keys} for {id} was not recognized."
                      .format(source=self._source_name, id=show.id, keys=attribute),
                      file=sys.stderr)
