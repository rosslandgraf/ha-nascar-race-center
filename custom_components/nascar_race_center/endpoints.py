"""Allowlisted anonymous CF endpoint catalog; never use restricted Swagger."""

BASE_URL = "https://cf.nascar.com"
LIVE_FEED = "/live/feeds/live-feed.json"


def schedule_path(year: int) -> str:
    """Route a season through the documented global race list."""
    if isinstance(year, bool) or not 1948 <= year <= 9999:
        raise ValueError("Invalid NASCAR season")
    return f"/cacher/{year}/race_list_basic.json"
