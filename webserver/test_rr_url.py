import pytest
from . import feed_server

app = feed_server.app
app.config['TESTING'] = True
tester = app.test_client()


@pytest.fixture()
def rr_urls():
    """Old podcast URLs still in use by iTunes and other podcast clients, as well as currently used URLs."""
    return [
        # Old URLs that were in use before. Ensure they still function properly.
        # Move an entry here when its show name changes (making the url old), and add the new name in the other section!
        "perrong-perrong",
        "ctrl-alt-del-podkast",
        "katarsis-podkast",
        "maggesinet",
        "laurbaer",
        "bankebrett",
        "PratRR",
        "Postkaakk",
        "mandag",
        "uillustrert-vitenskap",
        "triks-i-ludo",
        "Kara_sahara_podkast",
        "Exphil-losen",
        "byraaforeningen",
        "patirshda",
        "horror-night",
        #"alle-podkaster",
        "ReaktorRR",
        "globus-podkast",
        "bronch",
        "horror-night-english",

        # New URLs used by this system
        # Add a new entry whenever a new podcast is created or its name is changed!
        "fraarkivet",
        "ctrlaltdelete",
        "teknikertimen",
        "reservebenken",
        "nestenhelg",
        "sandimaskineriet",
        "denfolkeligetimen",
        "helsebror",
        "harselas",
        "perrongperrong",
        "katarsis",
        "mæggesinet",
        "faktapålaurbær",
        "bokbaren",
        "prat",
        "alleelskermandag",
        "uillustrertvitenskap",
        "triksiludo",
        "karafrasahara",
        "exphillosen",
        "byråforeningen",
        "påtirshda",
        "horrornight",
        "reaktor",
        "globus",
        "brønch",
        "horrornightenglish",
        "samfundsmøter",
        "kulturdepartementet",
        "feriekolonien",
        "trondheimmannsfengselspikemusikkorps",
        "soulmat",
        "badegristimen",
        "urtefitte",
        "nerdeprat",
        "ukesenderen",
        "tweed",
        "internettet",
        "garasjen",
        "gastromat",
        "aspik",
        "gretnegamlegubber",
        "nyhetsfredag",
        "palmehaven",
        "skammekroken",
        "sportsidiot",
        "studentlosen",
        "sekt",
        "institusjonen",
        "filmofil",
        "all",
        "alleepisoder",
        "allepisodes",
        "feber",    # example of feed without episodes
        "bermudashortstriangelet",
    ]


@pytest.fixture(params=rr_urls())
def rr_url(request):
    """Run the depending test once for each url in rr_urls."""
    return request.param


def test_feed_works(rr_url):
    """Make sure the given URL slug works (that is, returns 200 OK)"""
    url = "/{slug}".format(slug=rr_url)
    res = tester.head(url, follow_redirects=True)
    assert res.status_code in (200,), \
        "The URL {url} resulted in status code {status}, check ALTERNATE_SHOW_NAMES in webserver/alternate_show_names.py"\
            .format(url=url, status=res.status_code)
