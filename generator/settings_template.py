import datetime

# Set to True to enable debugging mode. Do not leave on in production!
DEBUG = True or False

# Default author name to use for episodes with no author
DEFAULT_AUTHOR = "NAME HERE"
DEFAULT_AUTHOR_EMAIL = "EMAIL HERE"

# EPISODE SOURCE SETTINGS

EPISODE_SOURCE = {
    # Base URL for the Radio Rest API (without trailing slash). Example: "http://example.org/v1"
    'RADIO_REST_API_URL': "URL",

    # Username for authenticating with the Radio Rest API
    'RADIO_REST_API_USERNAME': "USERNAME HERE",

    # Password for authenticating with the Radio Rest API
    'RADIO_REST_API_PASSWORD': "PASSWORD HERE",
}


# METADATA SOURCE SETTINGS

METADATA_SOURCE = {

    # CHIMERA SETTINGS
    'CHIMERA': {
        # Base URL for CHIMERA RADIO API (without trailing slash). Example: "http://example.org/radio/api"
        'API_URL': "URL",

        # Episodes from this date or newer will get metadata from Chimera.
        # datetime.date(year, month, day) or None
        'START_DATE': datetime.date(0, 0, 0)
    },

    # RADIOREVOLT.NO SETTINGS
    'RADIO_REVOLT': {
        # Base URL for RADIO REVOLT API (without trailing slash).
        'API_URL': "URL",

        # Episodes from this date or newer will get metadata from RadioRevolt.no.
        # datetime.date(year, month, day) or None
        'START_DATE': datetime.date(0, 0, 0)
    },

}
