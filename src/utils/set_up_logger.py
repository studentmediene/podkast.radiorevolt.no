import os.path
import logging.handlers
import sys
import gzip
import shutil
import warnings

streamHandler = None
rotatingHandler = None
mainStreamHandler = None


def set_up_logger():
    global streamHandler, rotatingHandler, mainStreamHandler
    _logger = logging.getLogger("")
    _logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(fmt='''\
    ================================================================================
    %(levelname)s while running SCRIPTNAME
        at %(asctime)s
        in %(pathname)s at line %(lineno)s
        PID: %(process)s, thread: %(thread)s, logger: %(name)s

    %(message)s
    '''.replace("SCRIPTNAME", sys.argv[0]))

    out_formatter = logging.Formatter(fmt='''\
    %(levelname)s: %(message)s''')

    def format_warnings(message, category, filename, lineno, line=None):
        return "(%s in %s:%s) %s%s" % (category.__name__, filename, lineno, message, "\n" + line if line else "")
    warnings.formatwarning = format_warnings
    warnings.filterwarnings("always")
    warnings.filterwarnings("ignore", message="unclosed <socket.socket",
                            category=ResourceWarning)
    warnings.filterwarnings("ignore", message="Size is set to 0")

    streamHandler = logging.StreamHandler()
    # Log records with this level or higher will always be printed
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

    # Save everything in this log, limit to 30 days
    rotatingHandler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "application.log"),
        when="midnight",
        backupCount=30,
    )
    # If you set this to logging.DEBUG, you'll be able to debug but the log will be
    # extremely huge
    rotatingHandler.setLevel(logging.INFO)
    rotatingHandler.setFormatter(log_formatter)
    rotatingHandler.namer = namer
    rotatingHandler.rotator = rotator
    _logger.addHandler(rotatingHandler)

    # Duplicate the important records in a separate file, with more backups
    rotatingImportantHandler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(os.path.dirname(__file__), "..", "..", "data",
                     "application.warnings.log"),
        when="midnight",
        backupCount=180,
    )
    rotatingImportantHandler.setLevel(logging.WARNING)
    rotatingImportantHandler.setFormatter(log_formatter)
    rotatingImportantHandler.namer = namer
    rotatingImportantHandler.rotator = rotator
    _logger.addHandler(rotatingImportantHandler)

    logging.captureWarnings(True)

    # Set up logger for the script that is being run
    main_logger = logging.getLogger("__main__")
    mainStreamHandler = logging.StreamHandler()
    main_logger.addHandler(mainStreamHandler)
    main_logger.setLevel(logging.DEBUG)
    # Default level for what is printed to the user
    mainStreamHandler.setLevel(logging.INFO)
    # Don't report anything twice, so don't print this at "__main__" if it'll get
    # printed out at "" (root_logger)
    mainStreamHandler.addFilter(
        lambda record: record.levelno < streamHandler.level)


# If the script wants to run as quiet, it simply needs to run
def quiet():
    mainStreamHandler.setLevel(logging.WARNING)
    streamHandler.setLevel(logging.WARNING)


def verbose():
    mainStreamHandler.setLevel(logging.DEBUG)
    streamHandler.setLevel(logging.DEBUG)
