import os.path
import datetime
import logging.handlers
import sys
import gzip
import shutil
import warnings
_logger = logging.getLogger("")
_logger.setLevel(logging.INFO)
log_formatter = logging.Formatter(fmt='''\
================================================================================
%(levelname)s while running SCRIPTNAME
    at %(asctime)s
    in %(pathname)s at line %(lineno)s

%(message)s
'''.replace("SCRIPTNAME", sys.argv[0]))

out_formatter = logging.Formatter(fmt='''\
%(levelname)s: %(message)s''')

def format_warnings(message, category, filename, lineno, line=None):
    return "(%s) %s\n" % (category.__name__, message)
warnings.formatwarning = format_warnings

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.WARNING)
streamHandler.setFormatter(out_formatter)
_logger.addHandler(streamHandler)


# Make sure we compress the log files (they can get quite big otherwise)
def namer(name):
    return name + ".gz"


def rotator(source, dest):
    with open(source, "rb") as sf:
        with gzip.open(dest, "wb") as df:
            shutil.copyfileobj(sf, df)
    os.remove(source)

rotatingHandler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(os.path.dirname(__file__), "..", "data", "application.log"),
    when="midnight",
    atTime=datetime.time(),
    backupCount=180,
)
rotatingHandler.setLevel(logging.WARNING)
rotatingHandler.setFormatter(log_formatter)
rotatingHandler.namer = namer
rotatingHandler.rotator = rotator
_logger.addHandler(rotatingHandler)

logging.captureWarnings(True)
