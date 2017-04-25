import datetime, pytz, os.path, threading
from podgen import Person, Category

__all__ = [
    "DEBUG",
    "DEFAULT_AUTHORS",
    "DEFAULT_WEBMASTER",
    "OWNER",
    "DEFAULT_SHORT_FEED_DESCRIPTION",
    "DEFAULT_WEBSITE",
    "URL_REDIRECTION_SOUND_URL",
    "URL_REDIRECTION_ARTICLE_URL",
    "CANCEL",
    "SHOW_SOURCE",
    "EPISODE_SOURCE",
    "METADATA_SOURCE",
    "BYPASS_EPISODE",
    "BYPASS_SHOW",
    "ALL_EPISODES_FEED_METADATA",
    "DEFAULT_CATEGORY",
    "DEFAULT_EXPLICIT",
    "MARK_OLD_AS_COMPLETE",
]
# TODO: Add fields for metadata for the all episodes feed (see generate_feed.py)
# Remove the hash symbol and space from the beginning of the following line
# from .settings_template import *

# Set to True to enable debugging mode, False to disable. Do not leave on in production!
DEBUG = False

# Set to True to mark old podcasts as completed. Doing so means an old podcast can never be started again later, since a
# completed podcast is supposed to never be updated again. Set to False to never mark a podcast as completed.
MARK_OLD_AS_COMPLETE = False

# Default email address for who to contact regarding content in a show.
DEFAULT_AUTHORS = [Person("Example Radio", "editor@example.org")]
# Default email address for who to contact regarding technical aspects of the podcast feed.
DEFAULT_WEBMASTER = Person("Radio Technique", "it@example.org")
# Name and email for the podcast owner, which will be contacted by iTunes for questions, problems etc.
# regarding the podcasts
OWNER = Person("Example Radio", "it@example.org")

# Default short description to use on shows with no description.
DEFAULT_SHORT_FEED_DESCRIPTION = "Podcast from Example Radio"
# Default website to use on shows with no website.
DEFAULT_WEBSITE = "http://example.org"
# Whether shows are inappropriate for children by default (True) or not (False)
DEFAULT_EXPLICIT = False
# Default category (see https://help.apple.com/itc/podcasts_connect/#/itc9267a2f12 for alternatives, use the normal
# alternative without escaping)
DEFAULT_CATEGORY = Category("Education", "Higher Education")

# Metadata for the feed with all episodes. See keyword arguments to Show() for
# allowed keys
ALL_EPISODES_FEED_METADATA = {
    "name": "All podcasts from Example Radio",
    "description": "All podcast episodes from Example Radio",
    "image": "http://static.example.org/all.png",
    # Add more if you like, see http://podgen.readthedocs.io/en/latest/user/basic_usage_guide/part_1.html
}

# URL redirection service
# This works by defining two mapping functions: one for podcast sound urls, one for article urls.
# The mapping function must take exactly two arguments: the original url and the Episode object.
# It must return a string with the absolute url which should be used in the original urls' place.
# Note that this just changes the URLs in the feed; the actual redirection service must be implemented outside of
# generator (the webserver implements this).
# Setting it to None disables the URL redirection.
URL_REDIRECTION_SOUND_URL = None
URL_REDIRECTION_ARTICLE_URL = None

# Do not modify
CANCEL = threading.Event()


# SHOW SOURCE SETTINGS

SHOW_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v2"
    'RADIO_REST_API_URL': "URL HERE",

    # Username for authenticating with the Radio Rest API
    'RADIO_REST_API_USERNAME': "USERNAME HERE",

    # Password for authenticating with the Radio Rest API
    'RADIO_REST_API_PASSWORD': "PASSWORD HERE",
}


# EPISODE SOURCE SETTINGS

current_folder = os.path.dirname(__file__)

EPISODE_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v2"
    # Reuse value from SHOW_SOURCE
    'RADIO_REST_API_URL': SHOW_SOURCE['RADIO_REST_API_URL'],
}

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
    'RadioRevolt_no': {
        # Base URL for RADIO REVOLT API (without trailing slash).
        'API_URL': "URL",
        # URL used to construct a show's website; %s will be replaced by its slug
        'SHOW_WEBSITE_TEMPLATE': "http://example.com/programs/%s/",
        'START_DATE': datetime.date(2016, 8, 29),
    },
    'ManualChanges': {
        # Path to the configuration file used by ManualChanges for episodes.
        # Default is metadata_sources/episode/manual_changes.json (relative to this directory).
        'EPISODE_CONFIG': os.path.join(os.path.dirname(__file__), "metadata_sources", "episode", "manual_changes.json"),

        # Path to the configuration file used by ManualChanges for shows.
        # Default is metadata_sources/show/manual_changes.json (relative to this directory).
        'SHOW_CONFIG': os.path.join(os.path.dirname(__file__), "metadata_sources", "show", "manual_changes.json"),
    },
    'SetDefaultImageURL': {
        # Absolute URL to the default image
        'IMAGE': "http://example.com/default.png",
    },

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

