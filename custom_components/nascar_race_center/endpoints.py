"""Allowlisted anonymous CF endpoint catalog; never use restricted Swagger."""

import re

from .history_models import HistoricalRaceKey, HistoryDataset

BASE_URL = "https://cf.nascar.com"
LIVE_FEED = "/live/feeds/live-feed.json"
LIVE_PITS = "/live/feeds/live-pit-data.json"
LIVE_STAGES = "/live/feeds/live-stage-points.json"
LIVE_POINTS = "/live/feeds/live-points.json"
DRIVERS = "/cacher/drivers.json"
TRACKS = "/cacher/tracks.json"

_HISTORY_FILES = {
    HistoryDataset.WEEKEND: "weekend-feed",
    HistoryDataset.LAPS: "lap-times",
    HistoryDataset.NOTES: "lap-notes",
    HistoryDataset.AVERAGES: "lap-averages",
    HistoryDataset.PITS: "live-pit-data",
    HistoryDataset.STAGES: "live-stage-points",
}
_HISTORY_PATH = re.compile(
    r"/(?:cacher/([0-9]{4})/([123])/([1-9][0-9]{0,10})/"
    r"(weekend-feed|lap-times|lap-notes|lap-averages|live-pit-data|live-stage-points)"
    r"|loopstats/prod/([0-9]{4})/([123])/([1-9][0-9]{0,10}))\.json"
)


def historical_path(key: HistoricalRaceKey, dataset: HistoryDataset) -> str:
    """Only explicitly selected race/feed keys; coverage remains unverified."""
    if not isinstance(dataset, HistoryDataset):
        raise ValueError("Unsupported historical dataset")
    if dataset == HistoryDataset.LOOP:
        return f"/loopstats/prod/{key.season}/{key.series_id}/{key.race_id}.json"
    prefix = f"/cacher/{key.season}/{key.series_id}/{key.race_id}"
    return f"{prefix}/{_HISTORY_FILES[dataset]}.json"


def is_historical_path(path: str) -> bool:
    """Validate the full transport allowlist, including season/ID bounds."""
    match = _HISTORY_PATH.fullmatch(path)
    if match is None:
        return False
    values = match.groups()[:3] if match.group(1) else match.groups()[4:]
    try:
        HistoricalRaceKey(*(int(v) for v in values))
    except ValueError, TypeError:
        return False
    return True


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
