"""Allowlisted anonymous CF endpoint catalog; never use restricted Swagger."""

BASE_URL = "https://cf.nascar.com"
LIVE_FEED = "/live/feeds/live-feed.json"
LIVE_PITS = "/live/feeds/live-pit-data.json"
LIVE_STAGES = "/live/feeds/live-stage-points.json"
LIVE_POINTS = "/live/feeds/live-points.json"
DRIVERS = "/cacher/drivers.json"
TRACKS = "/cacher/tracks.json"


def schedule_path(year: int) -> str:
    """Route a season through the documented global race list."""
    if isinstance(year, bool) or not 1948 <= year <= 9999:
        raise ValueError("Invalid NASCAR season")
    return f"/cacher/{year}/race_list_basic.json"


def schedule_feed_path(year: int, series_id: int) -> str:
    """Build the owner-reported per-series season session feed path."""
    schedule_path(year)
    if isinstance(series_id, bool) or series_id not in (1, 2, 3):
        raise ValueError("Unsupported national series")
    return f"/cacher/{year}/{series_id}/schedule-feed.json"
