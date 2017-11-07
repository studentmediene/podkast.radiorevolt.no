from datetime import time, timezone, datetime


def date2dt(date):
    """Convert date into timezone-aware datetime (with time=UTC midnight)."""
    midnight = time(tzinfo=timezone.utc)
    return datetime.combine(date, midnight)
