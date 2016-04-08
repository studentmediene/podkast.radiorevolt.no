from .. import EpisodeMetadataSource
from cached_property import cached_property
import json
import os.path
import sys
from datetime import datetime


class ManualChanges(EpisodeMetadataSource):

    @staticmethod
    def _get_key(episode):
        return str(episode.sound_url)

    @cached_property
    def _config_file(self):
        return self.settings['EPISODE_CONFIG']

    @cached_property
    def data(self):
        try:
            return json.load(open(self._config_file))
        except IOError as e:
            print("WARNING: ManualChanges is added as a metadata source for episodes, but the configuration file "
                  "{file} could not be loaded. \nDetails: {e}".format(file=self._config_file, e=e), file=sys.stderr)
            return None
        except ValueError as e:
            print("WARNING: There is an error in {file}.\nDetails: {e}".format(file=self._config_file, e=e),
                  file=sys.stderr)
            return None
        except KeyError:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "settings.py"))
            print("WARNING: No configuration file is configured for episode/ManualChanges.\n"
                  "Ensure the setting EPISODE_CONFIG is set for METADATA_SOURCE['ManualChanges'] "
                  "in {path}.".format(path=path),
                  file=sys.stderr)

    def accepts(self, episode) -> bool:
        try:
            return super().accepts(episode) and self._get_key(episode) in self.data
        except TypeError:
            return False

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
        # TODO: Issue a warning if there are unrecognized keys in metadata
