import pytest
from . import feed_server, settings
from generator import show_source as source
import urllib.parse

app = feed_server.app
app.config['TESTING'] = True
tester = app.test_client()


@pytest.fixture
def show_ids():
    s = source.ShowSource()
    shows = s.shows
    return list(shows.keys())


def test_api_help():
    res = tester.get("/api/")
    data = res.data.decode('utf-8')
    assert res.status_code == 200
    assert "/api/url/" in data
    assert "/api/slug/" in data


def test_api_url_help():
    res = tester.get("/api/url/")
    data = res.data.decode('utf-8')
    assert res.status_code == 200
    assert "/api/url/" in data


def get_test_params_for_url():
    params = list(settings.SHOW_CUSTOM_URL.keys())
    params = params[:min(len(params), 10)]
    shows = show_ids()
    params.extend(shows[:min(len(shows), 10)])
    return params


@pytest.fixture(params=get_test_params_for_url())
def slug(request):
    """Test with max 10 DigAS IDs and max 10 keys from SHOW_CUSTOM_URL."""
    return request.param


def test_api_url_works(slug):
    res = tester.get("/api/url/{slug}".format(slug=slug))
    assert res.status_code == 200
    res2 = tester.head(urllib.parse.urlparse(res.data).path)
    assert res2.status_code == 200


def test_api_url_not_found():
    res = tester.get("/api/url/thisdoesnotexist")
    assert res.status_code == 404


@pytest.fixture(params=[
    ("UPPErCAsE", "uppercase"),  # Test case
    ("  t e s t    sp  ace s  ", "testspaces"),  # Test removal of spaces
    ("t(his)_is_a_\\%23test4(!)", "thisisatest4"),  # Test removal of special characters but not numbers
    ("     \\%23", ""),  # Test empty resulting string
])
def convert_case(request):
    return request.param


def test_api_slug_help():
    res = tester.get("/api/slug/")
    data = res.data.decode('utf-8')
    assert res.status_code == 200
    assert "/api/slug/" in data


def test_api_slug_works(convert_case):
    res = tester.get("/api/slug/{to_convert}".format(to_convert=convert_case[0]))
    data = res.data.decode('utf-8')
    assert res.status_code == 200
    assert "/{converted}".format(converted=convert_case[1]) in data