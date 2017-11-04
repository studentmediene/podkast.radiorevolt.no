from datetime import datetime


def parse_date(s):
    """Parse date in format YYYY-MM-DD into datetime."""
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d")
