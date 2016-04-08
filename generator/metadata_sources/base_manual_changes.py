from cached_property import cached_property
import json
import os.path
import sys
from abc import ABCMeta, abstractproperty, abstractstaticmethod


class BaseManualChanges(metaclass=ABCMeta):
    @abstractproperty
    def _is_episode_source(self):
        pass

    @cached_property
    def _source_name(self):
        """str: Name used to identify which source is used."""
        return "episode/MetadataSource" if self._is_episode_source else "show/MetadataSource"

    @abstractproperty
    def _config_file_settings_key(self):
        pass

    @cached_property
    def _config_file(self):
        """Absolute path to the configuration file used by this source."""
        return self.settings[self._config_file_settings_key]

    @abstractstaticmethod
    def _get_key(self, obj):
        """Get the key used to identify the given epsiode or show."""
        pass

    @cached_property
    def data(self):
        try:
            return json.load(open(self._config_file))
        except IOError as e:
            print("WARNING: {source} is added as a metadata source, but the configuration file "
                  "{file} could not be loaded. \nDetails: {e}"
                  .format(file=self._config_file, e=e, source=self._source_name), file=sys.stderr)
            return None
        except ValueError as e:
            print("WARNING: There is an error in {file}.\nDetails: {e}".format(file=self._config_file, e=e),
                  file=sys.stderr)
            return None
        except KeyError:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "settings.py"))
            print("WARNING: No configuration file is configured for {source}.\n"
                  "Ensure the setting {setting} is set for METADATA_SOURCE['ManualChanges'] "
                  "in {path}.".format(path=path, source=self._source_name, setting=self._config_file_settings_key),
                  file=sys.stderr)
            return None

    def accepts(self, obj) -> bool:
        try:
            return super().accepts(obj) and self._get_key(obj) in self.data
        except TypeError:
            return False

    def check_for_unrecognized_keys(self, metadata, recognized_keys, id):
        unrecognized_keys = set(metadata.keys()) - recognized_keys
        if unrecognized_keys:
            print("WARNING {source}: Some attributes for {id} were not recognized, namely {keys}."
                  .format(source=self._source_name, id=id, keys=unrecognized_keys),
                  file=sys.stderr)
