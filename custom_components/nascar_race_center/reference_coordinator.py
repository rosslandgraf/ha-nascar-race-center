"""Slow reference updates whose failures never invalidate race schedules."""

import logging
from dataclasses import dataclass
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import REFERENCE_INTERVAL
from .models import ProviderError
from .reference import Driver, Track
from .reference_provider import ReferenceProvider

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReferenceData:
    """Last successful directories with independent availability and freshness."""

    drivers: dict[int, Driver]
    tracks: dict[int, Track]
    failed_feeds: frozenset[str]
    updated_at: dict[str, datetime]


class ReferenceCoordinator(DataUpdateCoordinator[ReferenceData]):
    """Share one daily driver/track request across favorites and calendars."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, provider: ReferenceProvider
    ) -> None:
        """Register timer ownership with the entry before the first refresh."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="NASCAR reference data",
            update_interval=REFERENCE_INTERVAL,
        )
        self.provider = provider
        self.data = ReferenceData({}, {}, frozenset({"drivers", "tracks"}), {})
        self.last_error_status: dict[str, int | None] = {}

    async def _async_update_data(self) -> ReferenceData:
        """Retain last-good metadata while identifying each failed directory."""
        drivers = self.data.drivers
        tracks = self.data.tracks
        updated = dict(self.data.updated_at)
        failed: set[str] = set()
        self.last_error_status = {}
        try:
            rows = await self.provider.async_get_drivers()
            drivers = {row.driver_id: row for row in rows}
            updated["drivers"] = dt_util.utcnow()
        except ProviderError as err:
            failed.add("drivers")
            self.last_error_status["drivers"] = err.status
            _LOGGER.debug("NASCAR driver directory unavailable: %s", err)
        try:
            venues = await self.provider.async_get_tracks()
            tracks = {row.track_id: row for row in venues}
            updated["tracks"] = dt_util.utcnow()
        except ProviderError as err:
            failed.add("tracks")
            self.last_error_status["tracks"] = err.status
            _LOGGER.debug("NASCAR track directory unavailable: %s", err)
        # Coordinator success describes the refresh completing. Consumers use
        # failed_feeds and per-feed timestamps rather than treating this as a
        # claim that every directory is currently available.
        return ReferenceData(drivers, tracks, frozenset(failed), updated)
