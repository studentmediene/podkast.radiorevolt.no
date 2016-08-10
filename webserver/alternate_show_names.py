# This dictionary is not used during normal operation.
# However, you can use it to import earlier urls into podcast-feed-gen.

# HOW TO USE:
# 1. Add a line in the dictionary which looks like:
#   "old_slug": digas_id,
#          - OR -
#   "old_slug": "new_slug"

# 2. Repeat step 1 for each old URL you want to import.

# 3. While you're in the parent directory (relative to this file), run:

#   python -m webserver.alternate_show_names

# 4. Confirm that this works by visiting the URLs in a browser while running the
#    server. Note that they are case insensitive.

# WARNING: Once you've put podcast-feed-gen into production, you won't need to
# add changes here. Instead, changes in show name are noticed and taken care of,
# ensuring that all old URLs work. YOU DO NOT NEED TO CARE ABOUT
# ALTERNATE_SHOW_NAMES, EXCEPT WHEN NEEDING TO ADD OLD URLS WHEN SETTING UP
# PODCAST-FEED-GEN!!!
ALTERNATE_SHOW_NAMES = {
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

# Those are alternate names for the special "all episodes" feed
ALTERNATE_ALL_EPISODES_FEED_NAME = {
    "alleepisoder",
    "allepisodes",
    "*",
}


def get_sluglist(id_or_slug, sluglist_cls):
    if isinstance(id_or_slug, int):
        # Is id
        return sluglist_cls.from_id(id_or_slug)
    else:
        # Is slug
        return sluglist_cls.from_slug(id_or_slug.lower().strip())


def populate_url_service():
    from .slug_list import SlugList
    from webserver.no_such_slug import NoSuchSlug
    for slug, target in ALTERNATE_SHOW_NAMES.items():
        try:
            sl = get_sluglist(target, SlugList)
            sl.prepend(slug.lower().strip())
            sl.commit()
        except NoSuchSlug:
            print("Id or slug %s not found in database. Try running \n"
                  "py.test webserver/test_rr_url.py\n to populate the db.")

if __name__ == '__main__':
    populate_url_service()
