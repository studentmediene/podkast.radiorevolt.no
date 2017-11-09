import logging
from . import EpisodeProcessor
from ..base_manual_changes import BaseManualChanges
from cached_property import threaded_cached_property as cached_property
import json
import os.path
import sys
from datetime import datetime, timedelta
from podgen import Person
logger = logging.getLogger(__name__)


class ManualChanges(BaseManualChanges, EpisodeProcessor):
    """
    Class for making manual changes to episodes on an episode to episode basis.

    Settings:
        episode_file: Path to json-file with manual changes to make, either
            absolute or relative to this folder.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def _is_episode_source(self):
        return True

    @cached_property
    def _config_file_settings_key(self):
        return "episode_file"

    @cached_property
    def _config_file_relative_to(self):
        return os.path.dirname(__file__)

    def accepts(self, episode) -> bool:
        return super().accepts(episode)

    @staticmethod
    def _get_key(episode):
        return str(episode.media.url)

    def populate(self, episode) -> None:
        metadata = self.data[self._get_key(episode)]

        for attribute, value in metadata.items():
            if hasattr(episode, attribute):
                if attribute == "publication_date":
                    try:
                        episode.publication_date = datetime.strptime(metadata['publication_date'], "%Y-%m-%d %H:%M:%S %z")
                    except ValueError:
                        logger.warning("Date %s in file %s could not be parsed, so it was ignored. "
                            "Make sure it's on the following form (±HHMM being timezone offset): "
                            "YYYY-MM-DD HH:MM:SS ±HHMM", metadata['date'], self._config_file)
                elif attribute == "authors":
                    authors = [Person(p.get('name'), p.get('email')) for p in value]
                    episode.authors = authors
                elif attribute.startswith("media."):
                    media_attribute = attribute[6:]
                    if media_attribute == "duration":
                        # Convert to datetime.timedelta
                        splitted = value.split(":")
                        if len(splitted) == 3:
                            duration = timedelta(hours=splitted[0],
                                minutes=splitted[1], seconds=splitted[2])
                        else:
                            duration = timedelta(minutes=splitted[0],
                                                 seconds=splitted[1])
                        episode.media.duration = duration
                    else:
                        setattr(episode.media, media_attribute, value)
                else:
                    setattr(episode, attribute, value)
            else:
                logger.warning("WARNING %s: Attribute %s for %s was not recognized.",
                      self._source_name, attribute, episode.media.url)
