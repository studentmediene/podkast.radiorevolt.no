from .skip_future import SkipFutureEpisodes
from .. import SkipEpisode
from ... import Episode, Show
from datetime import datetime, timedelta
import pytz
from functools import wraps
import pytest


def setup_show() -> Show:
    return Show("Example", 0)


@pytest.fixture()
def episode():
    """Initialize Episode with the date set to be now."""
    test_show = setup_show()
    return Episode("http://example.org", "My test sound", test_show, datetime.now(pytz.utc))


@pytest.fixture()
def skip_future_episode():
    """Initialize SkipFutureEpisode."""
    return SkipFutureEpisodes()


@pytest.fixture()
def now():
    """Timezone-aware datetime representing now."""
    return datetime.now(pytz.timezone("Europe/Oslo"))


@pytest.fixture()
def next_moment():
    """Timezone-aware datetime representing now +1 second."""
    return now() + timedelta(seconds=1)


def test_current_date_not_accepted(episode, skip_future_episode, now):
    episode.date = now
    assert not skip_future_episode.accepts(episode)


def test_future_date_not_accepted(episode, skip_future_episode, next_moment):
    """Assumes this test runs in under one second."""
    episode.date = next_moment
    assert skip_future_episode.accepts(episode)


def test_skipping(episode, skip_future_episode, next_moment):
    episode.date = next_moment
    with pytest.raises(SkipEpisode):
        if skip_future_episode.accepts(episode):
            skip_future_episode.populate(episode)
