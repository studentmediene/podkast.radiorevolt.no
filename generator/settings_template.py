import datetime, pytz, os.path, threading

__all__ = [
    "DEBUG",
    "DEFAULT_EDITORIAL_EMAIL",
    "DEFAULT_TECHNICAL_EMAIL",
    "OWNER_NAME",
    "OWNER_EMAIL",
    "DEFAULT_SHORT_FEED_DESCRIPTION",
    "DEFAULT_WEBSITE",
    "URL_REDIRECTION_SOUND_URL",
    "URL_REDIRECTION_ARTICLE_URL",
    "QUIET",
    "CANCEL",
    "SHOW_SOURCE",
    "EPISODE_SOURCE",
    "METADATA_SOURCE",
    "BYPASS_EPISODE",
    "BYPASS_SHOW",
    "EPISODE_DURATIONS_DB",
    "EPISODE_SIZES_DB",
    "ALL_EPISODES_FEED_TITLE",
]
# Remove the hash symbol and space from the beginning of the following line
# from .settings_template import *

# Set to True to enable debugging mode, False to disable. Do not leave on in production!
DEBUG = False

# Default email address for who to contact regarding content in a show.
DEFAULT_EDITORIAL_EMAIL = "editor@example.org"
# Default email address for who to contact regarding technical aspects of the podcast feed.
DEFAULT_TECHNICAL_EMAIL = "it@example.org"
# Name and email for the podcast owner, which will be contacted by iTunes for questions, problems etc.
# regarding the podcasts
OWNER_NAME = "Example Radio"
OWNER_EMAIL = "it@example.org"

# Default short description to use on shows with no description.
DEFAULT_SHORT_FEED_DESCRIPTION = "Podcast from Example Radio"
# Default website to use on shows with no website.
DEFAULT_WEBSITE = "http://example.org"

# Default title for the special feed with episodes from all shows
ALL_EPISODES_FEED_TITLE = "All podcast episodes from Example Radio"

# URL redirection service
# This works by defining two mapping functions: one for podcast sound urls, one for article urls.
# The mapping function must take exactly two arguments: the original url and the Episode object.
# It must return a string with the absolute url which should be used in the original urls' place.
# Note that this just changes the URLs in the feed; the actual redirection service must be implemented outside of
# generator (the webserver implements this).
# Setting it to None disables the URL redirection.
URL_REDIRECTION_SOUND_URL = None
URL_REDIRECTION_ARTICLE_URL = None

# Determines whether progress information should be printed. Modified by command line options.
QUIET = True
# Do not modify
CANCEL = threading.Event()


# SHOW SOURCE SETTINGS

SHOW_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v1"
    'RADIO_REST_API_URL': "URL HERE",

    # Username for authenticating with the Radio Rest API
    'RADIO_REST_API_USERNAME': "USERNAME HERE",

    # Password for authenticating with the Radio Rest API
    'RADIO_REST_API_PASSWORD': "PASSWORD HERE",
}


# EPISODE SOURCE SETTINGS

current_folder = os.path.dirname(__file__)

EPISODE_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v1"
    # Reuse value from SHOW_SOURCE
    'RADIO_REST_API_URL': SHOW_SOURCE['RADIO_REST_API_URL'],
}

# EPISODE SETTINGS

# Where to store the database file for caching episode durations. A new file will be created if it doesn't exist.
# Defaults to episode_durations.db in this folder, but you might want to place it somewhere else so you can
# restrict the program's permissions to edit its sources.
EPISODE_DURATIONS_DB = os.path.join(current_folder, "..", "data", "episode_durations.db")

# Where to store the database file for caching episode sizes. A new file will be created if it doesn't exist.
# Defaults to episode_sizes.db in this folder. The above notes about security applies to this as well.
EPISODE_SIZES_DB = os.path.join(current_folder, "..", "data", "episode_sizes.db")


# METADATA SOURCE SETTINGS - key must match the class name.

# If an episode source and a show source shares their class name, they will share settings.

# Two special settings are START_DATE and END_DATE. With those, you can limit the source to accepting episodes which are
# published within the given range.
# If START_DATE is None, all episodes before END_DATE will be accepted.
# If END_DATE is None, all episodes after START_DATE will be accepted.
# If they're both None or one or zero of them are present, there will be no limits imposed in regards to episode date.
# When not None, they must be a timezone-aware instance of datetime.datetime. Syntax for date given in UTC:
# datetime.datetime(year, month, day, hour, minute, tzinfo=pytz.utc)

METADATA_SOURCE = {

    # CHIMERA SETTINGS
    'Chimera': {
        # Base URL for CHIMERA RADIO API (without trailing slash). Example: "http://example.org/radio/api"
        'API_URL': "URL",

        'START_DATE': datetime.datetime(2016, 4, 12, 0, 0, tzinfo=pytz.utc),

        'END_DATE': None,
    },

    # RADIOREVOLT.NO SETTINGS
    # TODO: Implement metadata source for RadioRevolt.no
    'RadioRevolt': {
        # Base URL for RADIO REVOLT API (without trailing slash).
        'API_URL': "URL",

        'START_DATE': datetime.date(2000, 1, 1),
    },
    'ManualChanges': {
        # Path to the configuration file used by ManualChanges for episodes.
        # Default is metadata_sources/episode/manual_changes.json (relative to this directory).
        'EPISODE_CONFIG': os.path.join(os.path.dirname(__file__), "metadata_sources", "episode", "manual_changes.json"),

        # Path to the configuration file used by ManualChanges for shows.
        # Default is metadata_sources/show/manual_changes.json (relative to this directory).
        'SHOW_CONFIG': os.path.join(os.path.dirname(__file__), "metadata_sources", "show", "manual_changes.json"),
    }

}

# BYPASS - define which episodes and shows should be bypassed by the different metadata sources.

# There are two variables, BYPASS_EPISODE and BYPASS_SHOW, which both are dictionaries.
# In those dictionaries, the metadata source class name is used as key and a set with episodes or
# shows to bypass are used as values.

# Episodes to bypass are identified by their sound_url, that is the URL where the podcast episode can be found.
# Shows to bypass are identified by their show_id, that is the DigAS ID used to identify that show.

BYPASS_EPISODE = {
    'Chimera': {

    },
    'SkipFutureEpisodes': {

    },
}
BYPASS_SHOW = {
    'Chimera': {

    },
    'ManualChanges': {

    },
}

