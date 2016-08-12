import logging
from cached_property import threaded_cached_property as cached_property
import json
import os.path
import sys
from abc import ABCMeta, abstractproperty, abstractstaticmethod

logger = logging.getLogger(__name__)

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
        f = None
        try:
            f = open(self._config_file)
            return json.load(f)
        except IOError:
            logger.exception("%s is added as a metadata source, but the configuration file "
                             "%s could not be loaded.",
                             self._source_name, self._config_file)
            return None
        except ValueError:
            logger.exception("An error occurred while parsing %s. Check the syntax!", self._config_file)
            return None
        except KeyError:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "settings.py"))
            logger.error("No configuration file is configured for %s. "
                         "Ensure the setting %s is set for METADATA_SOURCE['ManualChanges'] "
                         "in %s.", self._source_name, self._config_file_settings_key, path)
            return None
        finally:
            if f:
                f.close()

    def accepts(self, obj) -> bool:
        try:
            return super().accepts(obj) and self._get_key(obj) in self.data
        except TypeError:
            return False

    def check_for_unrecognized_keys(self, metadata, recognized_keys, id):
        unrecognized_keys = set(metadata.keys()) - recognized_keys
        if unrecognized_keys:
            logger.warning("%s: Some attributes for %s were not recognized, namely %s.",
                        self._source_name, id, unrecognized_keys)
