from .show_metadata_source import ShowMetadataSource
import pytest
from generator.test_utils import *
import datetime


class BasicMetadataSource(ShowMetadataSource):
    def populate(self, show) -> None:
        return super().populate(show)

    def accepts(self, show) -> bool:
        return super().accepts(show)


@pytest.fixture()
def source_with_bypass() -> BasicMetadataSource:
    """Initialize BasicMetadataSource with 3 in its bypass-set."""
    return BasicMetadataSource(dict(), {3})


@pytest.fixture()
def source_without_bypass() -> BasicMetadataSource:
    """Initialize BasicMetadataSource with empty bypass-set."""
    return BasicMetadataSource(dict(), set())


@pytest.fixture()
def show_bypassed_id():
    """Show with id 3 (which is added to the bypass list of source_with_bypass)"""
    my_show = show()
    my_show.show_id = 3
    return my_show


def test_bypass(source_with_bypass, show, show_bypassed_id):
    assert not source_with_bypass.accepts(show_bypassed_id)
    assert source_with_bypass.accepts(show)


def test_no_bypass(source_without_bypass, show, show_bypassed_id):
    assert source_without_bypass.accepts(show_bypassed_id)
    assert source_without_bypass.accepts(show)


def test_settings_assigned():
    source = BasicMetadataSource({"testing": "something"}, set())
    assert "testing" in source.settings
    assert source.settings['testing'] == "something"
