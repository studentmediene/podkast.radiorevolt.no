import os.path as path

# Remove the hash and space at the beginning of the following line when creating settings.py
# from .settings_template import *

__all__ = [
    "OFFICIAL_WEBSITE",
    "DEBUG",
    "REDIRECT_DB_FILE",
]

# Set to True to enable debug mode. DO NOT LEAVE ON IN PRODUCTION!
DEBUG = False


# Website which you will be redirected to if you access / on the server.
OFFICIAL_WEBSITE = "http://radio.example.org"

# Path to the DB file used by the redirection service
REDIRECT_DB_FILE = path.abspath(path.join(path.dirname(__file__), "..", "data", "redirects.db"))
