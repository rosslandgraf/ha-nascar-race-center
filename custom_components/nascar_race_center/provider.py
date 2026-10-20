"""Swappable data providers; demonstration mode never makes network requests."""

from datetime import UTC, datetime
from typing import Protocol

from aiohttp import ClientSession

from .api import NascarApiClient
from .endpoints import LIVE_FEED, schedule_path
from .models import LiveSnapshot, Race, parse_live, parse_schedule


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
        self.api = NascarApiClient(session)

    async def async_get_schedule(self, year: int, series_id: int) -> tuple[Race, ...]:
        """Reuse one cached global response for all selected series."""
        payload = await self.api.async_get_json(schedule_path(year), minimum_ttl=3600)
        return parse_schedule(payload, series_id)

    async def async_get_live(self) -> LiveSnapshot | None:
        """Read session context without treating archived data as active."""
        return parse_live(await self.api.async_get_json(LIVE_FEED, minimum_ttl=60))


class DemoProvider:
    """Deterministic handmade examples, plainly marked as demonstration data."""

    async def async_get_schedule(self, year: int, series_id: int) -> tuple[Race, ...]:
        """Supply two fictional fixtures per selected series and season."""
        if series_id not in (1, 2, 3):
            raise ValueError("Unsupported national series")
        return (
            Race(
                series_id=series_id,
                race_id=year * 100 + series_id,
                name=f"Demo Series {series_id} Season Opener",
                start_time=datetime(year, 2, 15, 19, tzinfo=UTC),
                track="Demonstration Speedway",
            ),
            Race(
                series_id=series_id,
                race_id=year * 100 + series_id + 10,
                name=f"Demo Series {series_id} Finale",
                start_time=datetime(year, 11, 15, 19, tzinfo=UTC),
                track="Demonstration Speedway",
            ),
        )

    async def async_get_live(self) -> LiveSnapshot | None:
        """Demonstrate an empty feed, never a fabricated real live race."""
        return None
