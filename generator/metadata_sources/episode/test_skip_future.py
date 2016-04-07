from .skip_future import SkipFutureEpisodes
from .. import SkipEpisode
import pytest
from generator.test_utils import *


@pytest.fixture()
def skip_future_episode():
    """Initialize SkipFutureEpisode."""
    return SkipFutureEpisodes(dict(), set())


def test_current_date_not_accepted(episode, skip_future_episode, now):
    episode.date = now
    assert not skip_future_episode.accepts(episode)


def test_future_date_not_accepted(episode, skip_future_episode, next_moment):
    """Assumes this test runs in under one second."""
    episode.date = next_moment
    assert skip_future_episode.accepts(episode)


def test_bypass(episode, skip_future_episode, next_moment):
    episode.date = next_moment
    skip_future_episode.bypass.add(episode.sound_url)
    assert not skip_future_episode.accepts(episode)


def test_skipping(episode, skip_future_episode, next_moment):
    episode.date = next_moment
    with pytest.raises(SkipEpisode):
        if skip_future_episode.accepts(episode):
            skip_future_episode.populate(episode)
