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
# The URL to match is the key (without slashes).
# The new URL (without slashes) or the DigAS ID is the value.
# NOTE: None of those are case-sensitive.
# NOTE: When a program changes its name, add an entry with the old name without spaces and the new name without spaces.
# This way, old links will continue to work even after the name change.
# WARNING: Make sure you don't create a cycle (ie. "example": "example" or "example": "example2", "example2": "example")
# Such endless loops result in a 500 Internal Server Error when triggered.
SHOW_CUSTOM_URL = {
    # The following entries are specific for Radio Revolt. Remove them if you're not from Radio Revolt.
    # Compatibility with existing podcast URLs (not all are needed, but they're listed here so we know about them)
    "perrong-perrong": 2380,
    "teknikertimen": 2465,
    "ctrl-alt-del-podkast": 1615,
    "katarsis-podkast": 1617,
    "Reservebenken": 2512,
    "bokbaren": 1980,
    "FraArkivet": 2560,
    "maggesinet": 2341,
    "nestenhelg": 2412,
    "SandIMaskineriet": 2494,
    "DenFolkeligeTimen": 2447,
    "Helsebror": 2608,
    "harselas": 2467,
    "laurbaer": 2414,
    "bankebrett": 2242,
    "PratRR": 2589,
    "Postkaakk": 2445,
    "kulturdepartementet": 2339,
    "Feriekolonien": 2609,
    "TrondheimMannsfengselsPikemusikkorps": 2590,
    "badegristimen": 2247,
    "mandag": 2233,
    "uillustrert-vitenskap": 1957,
    "triks-i-ludo": 2245,
    "Soulmat": 2445,
    "Kara_sahara_podkast": 2424,
    "Exphil-losen": 2425,
    "urtefitte": 2383,
    "Nerdeprat": 2592,
    "Ukesenderen": 2438,
    "internettet": 2347,
    "byraaforeningen": 2345,
    "patirshda": 1520,
    "horror-night": 2338,
    #"alle-podkaster": None,
    "ReaktorRR": 2607,
    "tweed": 2410,
    "Garasjen": 2511,
    "filmofil": 232,
    "globus-podkast": 1977,
    "Institusjonen": 2539,
    "bronch": 2340,
    "GretneGamleGubber": 2541,
    "nyhetsfredag": 2002,
    "palmehaven": 2241,
    "Skammekroken": 2611,
    "sportsidiot": 2413,
    "sekt": 2250,
    "horror-night-english": 2350,
    "gastromat": 2003,
    "aspik": 2251,
    # Program name changes
    "postkåkk": "soulmat",
}
