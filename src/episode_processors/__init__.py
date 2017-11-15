import logging as _logging

from utils.find_modules import find_modules as _find_modules
from episode_processors._episode_processor import EpisodeProcessor
from episode_processors._skip_episode import SkipEpisode

_modules = _find_modules(__file__)

for module in _modules:
    try:
        exec("from {} import *".format(module))
    except Exception as e:
        _logging.exception("Error occurred while importing {}{}, skipping"
                           .format(__name__, module))
