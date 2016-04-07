import datetime, pytz

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

# Determines whether new episode duration should be calculated by default. Modified by command line options.
FIND_EPISODE_DURATIONS = False

# Determines whether progress information should be printed. Modified by command line options.
QUIET = True


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

EPISODE_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v1"
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
    # TODO: Implement metadata source for RadioRevolt.no
    'RadioRevolt': {
        # Base URL for RADIO REVOLT API (without trailing slash).
        'API_URL': "URL",

        'START_DATE': datetime.date(2000, 1, 1),
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

