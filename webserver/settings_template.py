# Remove the hash and space at the beginning of the following line when creating settings.py
# from .settings_template import *

__all__ = [
    "OFFICIAL_WEBSITE",
    "SHOW_CUSTOM_URL",
    "DEBUG",
]

# Set to True to enable debug mode. DO NOT LEAVE ON IN PRODUCTION!
DEBUG = False


# Website which you will be redirected to if you access / on the server.
OFFICIAL_WEBSITE = "http://radio.example.org"

# Define custom URLs for some shows
# The URL to match is the key, and the DigAS ID is the value.
SHOW_CUSTOM_URL = {

}
