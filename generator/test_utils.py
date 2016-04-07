from .show import Show
from .episode import Episode
import pytest
from datetime import datetime, timedelta
import pytz

__all__ = [
    'show',
    'episode',
    'now',
    'next_moment'
]


@pytest.fixture()
def show() -> Show:
    """Initialize Show with title "Example" and show_id 0."""
    return Show("Example", 0)


@pytest.fixture()
def episode():
    """Initialize Episode with the date set to be now."""
    test_show = show()
    return Episode("http://example.org", "My test sound", test_show, datetime.now(pytz.utc))


@pytest.fixture()
def now():
    """Timezone-aware datetime representing now."""
    return datetime.now(pytz.timezone("Europe/Oslo"))


@pytest.fixture()
def next_moment():
    """Timezone-aware datetime representing now +1 second."""
    return now() + timedelta(seconds=1)
