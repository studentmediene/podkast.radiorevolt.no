from ..utils.find_modules import find_modules as _find_modules
from ._episode_processor import EpisodeProcessor
from ._skip_episode import SkipEpisode
import logging as _logging

_modules = _find_modules(__file__)

for module in _modules:
    try:
        exec("from {} import *".format(module))
    except Exception as e:
        _logging.exception("Error occurred while importing {}{}, skipping"
                           .format(__name__, module))
