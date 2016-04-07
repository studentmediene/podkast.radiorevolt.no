from .episode_metadata_source import EpisodeMetadataSource
import pytest
from generator.test_utils import *
import datetime


class BasicMetadataSource(EpisodeMetadataSource):
    def populate(self, episode) -> None:
        return super().populate(episode)

    def accepts(self, episode) -> bool:
        return super().accepts(episode)


@pytest.fixture()
def source() -> BasicMetadataSource:
    """Initialize BasicMetadataSource, a bare-bones implementation of EpisodeMetadataSource."""
    return BasicMetadataSource(dict(), set())


@pytest.fixture()
def source_no_range() -> BasicMetadataSource:
    """BasicMetadataSource with START_DATE and END_DATE set to None."""
    my_source = source()
    my_source.settings['START_DATE'] = None
    my_source.settings['END_DATE'] = None
    return my_source


@pytest.fixture()
def source_start() -> BasicMetadataSource:
    """BasicMetadataSource with START_DATE set to yesterday and END_DATE set to None."""
    my_source = source()
    my_source.settings['START_DATE'] = now() - one_day()
    my_source.settings['END_DATE'] = None
    return my_source


@pytest.fixture()
def source_end() -> BasicMetadataSource:
    """BasicMetadataSource with START_DATE set to None and END_DATE set to tomorrow."""
    my_source = source()
    my_source.settings['START_DATE'] = None
    my_source.settings['END_DATE'] = now() + one_day()
    return my_source


@pytest.fixture()
def source_with_range() -> BasicMetadataSource:
    """BasicMetadataSource with START_DATE set to yesterday and END_DATE set to tomorrow."""
    my_source = source()
    my_source.settings['START_DATE'] = now() - one_day()
    my_source.settings['END_DATE'] = now() + one_day()
    return my_source


@pytest.fixture()
def episode_too_early():
    """Episode with date set to the day before yesterday."""
    my_episode = episode()
    my_episode.date -= (one_day() * 2)
    return my_episode


@pytest.fixture()
def episode_too_late():
    """Episode with date set to the day after tomorrow."""
    my_episode = episode()
    my_episode.date += (one_day() * 2)
    return my_episode


def one_day() -> datetime.timedelta:
    """Timedelta set to one day. Used by the fixtures."""
    return datetime.timedelta(days=1)


def test_accepts_no_range(episode, episode_too_early, episode_too_late, source):
    assert source.accepts(episode_too_early)
    assert source.accepts(episode)
    assert source.accepts(episode_too_late)


def test_accepts_none_range(episode, episode_too_early, episode_too_late, source_no_range):
    assert source_no_range.accepts(episode_too_early)
    assert source_no_range.accepts(episode)
    assert source_no_range.accepts(episode_too_late)


def test_accepts_start(episode, episode_too_early, episode_too_late, source_start):
    assert not source_start.accepts(episode_too_early)
    assert source_start.accepts(episode)
    assert source_start.accepts(episode_too_late)


def test_accepts_with_range(episode_too_early, episode, episode_too_late, source_with_range):
    assert not source_with_range.accepts(episode_too_early)
    assert source_with_range.accepts(episode)
    assert not source_with_range.accepts(episode_too_late)


def test_accepts_end(episode_too_early, episode, episode_too_late, source_end):
    assert source_end.accepts(episode_too_early)
    assert source_end.accepts(episode)
    assert not source_end.accepts(episode_too_late)


def test_accepts_bypass(episode, source, source_no_range, source_start, source_with_range, source_end):
    sources = [source, source_no_range, source_start, source_with_range, source_end]
    for tested_source in sources:
        tested_source.bypass.add(episode.sound_url)
        assert not tested_source.accepts(episode)
        tested_source.bypass.remove(episode.sound_url)
        assert tested_source.accepts(episode)

