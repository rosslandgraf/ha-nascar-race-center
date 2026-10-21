"""Swappable data providers; demonstration mode never makes network requests."""

from collections import OrderedDict
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Protocol

from aiohttp import ClientSession

from .api import NascarApiClient
from .endpoints import LIVE_FEED, schedule_feed_path, schedule_path
from .models import (
    LiveSnapshot,
    ProviderError,
    Race,
    Session,
    merge_schedule,
    parse_live,
    parse_schedule,
    parse_schedule_feed,
)


class RaceProvider(Protocol):
    """Small provider boundary shared by schedule and live coordinators."""

    async def async_get_schedule(self, year: int, series_id: int) -> tuple[Race, ...]:
        """Fetch a single selected series' schedule for a season."""
        ...

    async def async_get_live(self) -> LiveSnapshot | None:
        """Fetch the one series identified by the global live feed."""
        ...


class CFProvider:
    """Experimental CF adapter, selected only after explicit UI authorization."""

    def __init__(self, session: ClientSession) -> None:
        """Use Home Assistant's managed shared session."""
        self.api = NascarApiClient(session, max_cache_entries=16)
        self.parse_results: OrderedDict[str, str] = OrderedDict()
        self.schedule_details_failed: set[tuple[int, int]] = set()

    async def _read[T](
        self,
        path: str,
        ttl: int,
        parser: Callable[[object], T],
        *,
        key: str | None = None,
    ) -> T:
        """Separate transport, JSON and domain parsing without retaining raw data."""
        key = key or path
        self.parse_results[key] = "not_parsed"
        self.parse_results.move_to_end(key)
        while len(self.parse_results) > 24:
            self.parse_results.popitem(last=False)
        payload = await self.api.async_get_json(path, minimum_ttl=ttl)
        try:
            result = parser(payload)
        except ProviderError:
            self.parse_results[key] = "invalid"
            raise
        self.parse_results[key] = "parsed"
        return result

    async def async_get_schedule(self, year: int, series_id: int) -> tuple[Race, ...]:
        """Combine slow independent schedule feeds without losing usable races."""
        basic: tuple[Race, ...] | None = None
        basic_error: ProviderError | None = None
        try:
            basic = await self._read(
                schedule_path(year),
                3600,
                lambda payload: parse_schedule(payload, series_id, year=year),
                key=f"basic:{year}:{series_id}",
            )
        except ProviderError as err:
            basic_error = err
        # Only the current/requested adjacent season is retained in diagnostics.
        self.schedule_details_failed.intersection_update(
            key for key in self.schedule_details_failed if abs(key[0] - year) <= 1
        )
        try:
            detailed = await self._read(
                schedule_feed_path(year, series_id),
                21600,
                lambda payload: parse_schedule_feed(payload, series_id, year),
                key=f"sessions:{year}:{series_id}",
            )
            merged = merge_schedule(basic or (), detailed)
        except ProviderError:
            if self.parse_results.get(f"sessions:{year}:{series_id}") == "parsed":
                self.parse_results[f"sessions:{year}:{series_id}"] = "context_conflict"
            self.schedule_details_failed.add((year, series_id))
            if basic is not None:
                return basic
            assert basic_error is not None
            raise basic_error from None
        self.schedule_details_failed.discard((year, series_id))
        if basic is None and not detailed:
            # An optional feed with no enrichment cannot establish that the
            # authoritative season is empty or conceal its access/schema error.
            assert basic_error is not None
            raise basic_error
        return merged

    async def async_get_live(self) -> LiveSnapshot | None:
        """Read session context without treating archived data as active."""
        return await self._read(LIVE_FEED, 60, parse_live)


class DemoProvider:
    """Deterministic handmade examples, plainly marked as demonstration data."""

    async def async_get_schedule(self, year: int, series_id: int) -> tuple[Race, ...]:
        """Supply two fictional multi-day weekends per selected series."""
        if series_id not in (1, 2, 3):
            raise ValueError("Unsupported national series")
        races: list[Race] = []
        for race_id, label, month in (
            (year * 100 + series_id, "Season Opener", 2),
            (year * 100 + series_id + 10, "Finale", 11),
        ):
            start = datetime(year, month, 15, 19, tzinfo=UTC)
            sessions = tuple(
                Session(
                    session_id=f"demo:{series_id}:{year}:{race_id}:{kind}",
                    name=name,
                    kind=kind,
                    start_time=start + offset,
                    end_time=start + offset + duration,
                    notes="Fictional offline demonstration session",
                )
                for kind, name, offset, duration in (
                    (
                        "practice",
                        "Demo Practice",
                        timedelta(days=-2),
                        timedelta(hours=1),
                    ),
                    (
                        "qualifying",
                        "Demo Qualifying",
                        timedelta(days=-1),
                        timedelta(hours=1),
                    ),
                    ("race", "Demo Race", timedelta(), timedelta(hours=3)),
                )
            )
            races.append(
                Race(
                    series_id=series_id,
                    race_id=race_id,
                    name=f"Demo Series {series_id} {label}",
                    start_time=start,
                    track="Demonstration Speedway",
                    season=year,
                    track_id=99001,
                    sessions=sessions,
                )
            )
        return tuple(races)

    async def async_get_live(self) -> LiveSnapshot | None:
        """Demonstrate an empty feed, never a fabricated real live race."""
        return None
