import logging as _logging

from utils.find_modules import find_modules as _find_modules
from show_processors._show_processor import ShowProcessor
from show_processors._skip_show import SkipShow

_modules = _find_modules(__file__)

for module in _modules:
    try:
        exec("from {} import *".format(module))
    except Exception:
        _logging.exception("Error occurred while importing {}{}, skipping"
                           .format(__name__, module))

