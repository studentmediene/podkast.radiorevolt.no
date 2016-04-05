import datetime

# Set to True to enable debugging mode, False to disable. Do not leave on in production!
DEBUG = False

# Default email address for who to contact regarding content in a show.
DEFAULT_EDITORIAL_EMAIL = "editor@example.org"
# Default email address for who to contact regarding technical aspects of the podcast feed.
DEFAULT_TECHNICAL_EMAIL = "it@example.org"

# Default short description to use on shows with no description.
DEFAULT_SHORT_FEED_DESCRIPTION = "Podcast from Example Radio"
# Default website to use on shows with no website.
DEFAULT_WEBSITE = "http://example.org"

# Set to True to enable calculation of episode durations by default, False to disable.
# TODO: Implement behaviour where calculated episode durations are always used, but don't calculate new ones \
# unless we're a background task
FIND_EPISODE_DURATIONS = True


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


# METADATA SOURCE SETTINGS

METADATA_SOURCE = {

    # CHIMERA SETTINGS
    # TODO: Implement metadata source for Chimera
    'CHIMERA': {
        # Base URL for CHIMERA RADIO API (without trailing slash). Example: "http://example.org/radio/api"
        'API_URL': "URL",

        # Episodes from this date or newer will get metadata from Chimera.
        # datetime.date(year, month, day) or None
        'START_DATE': datetime.date(2000, 1, 1)
    },

    # RADIOREVOLT.NO SETTINGS
    # TODO: Implement metadata source for RadioRevolt.no
    'RADIO_REVOLT': {
        # Base URL for RADIO REVOLT API (without trailing slash).
        'API_URL': "URL",

        # Episodes from this date or newer will get metadata from RadioRevolt.no.
        # datetime.date(year, month, day) or None
        'START_DATE': datetime.date(2000, 1, 1)
    },

}
