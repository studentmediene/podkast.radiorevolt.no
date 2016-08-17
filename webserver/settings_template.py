import datetime

import os.path as path

# Remove the hash and space at the beginning of the following line when creating settings.py
# from .settings_template import *

__all__ = [
    "OFFICIAL_WEBSITE",
    "DEBUG",
    "REDIRECT_DB_FILE",
    "URL_DB_CONNECTION_PARAMS",
    "SOURCE_DATA_TTL",
    "FEED_TTL",
]

# Set to True to enable debug mode. DO NOT LEAVE ON IN PRODUCTION!
DEBUG = False

# How old source data (like list of shows, list of episodes, episode metadata)
# can be before it is discarded and reloaded from the source. How old data the
# clients can potentially get, is SOURCE_DATA_TTL + FEED_TTL.
SOURCE_DATA_TTL = datetime.timedelta(minutes=7)

# How long a feed's content can be served by a cache before it must be fetched
# from podcast-feed-gen again. Does not apply to /all.
FEED_TTL = datetime.timedelta(minutes=8)


# Website which you will be redirected to if you access / on the server.
OFFICIAL_WEBSITE = "http://radio.example.org"

# Path to the DB file used by the redirection service
REDIRECT_DB_FILE = path.abspath(path.join(path.dirname(__file__), "..", "data", "redirects.db"))

# Connection details for the URL PostgreSQL database.
URL_DB_CONNECTION_PARAMS = {
    # The host where the database is located. Remove the line if the host is the
    # same for both podcast-feed-gen and the PostgreSQL server.
    "host": "db.example.com",
    # Port to use for the connection. 5432 is the default.
    "port": 5432,
    # Database to use.
    "database": "urlredirect",
    # Username and password used to authenticate on the server.
    "user": "bob",
    "password": "password123",
}
