"""Independent schedule and live update loops with bounded polling."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    LIVE_IDLE_INTERVAL,
    LIVE_OFF_SEASON_INTERVAL,
    LIVE_STALE_AFTER,
    SCHEDULE_INTERVAL,
)
from .models import LiveSnapshot, ProviderError, Race
from .provider import RaceProvider

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScheduleData:
    """Schedules and per-series freshness; never substitute failed data with zero."""

    races: dict[int, tuple[Race, ...]]
    failed_series: frozenset[int]
    updated_at: dict[int, datetime]


class ScheduleCoordinator(DataUpdateCoordinator[ScheduleData]):
    """Refresh metadata infrequently, independently for each selected series."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        provider: RaceProvider,
        series: tuple[int, ...],
    ) -> None:
        """Initialize one slow update loop for all selected schedules."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="NASCAR schedules",
            update_interval=SCHEDULE_INTERVAL,
        )
        self.provider = provider
        self.series = series
        self.data = ScheduleData(
            races={}, failed_series=frozenset(series), updated_at={}
        )
        self.last_error_status: int | None = None
        self._unsub_boundary: Callable[[], None] | None = None

    async def async_shutdown(self) -> None:
        """Release the local race-boundary timer along with provider polling."""
        if self._unsub_boundary is not None:
            self._unsub_boundary()
            self._unsub_boundary = None
        await super().async_shutdown()

    @callback
    def _schedule_next_boundary(self, data: ScheduleData) -> None:
        """Advance local next-race states without an additional HTTP request."""
        if self._unsub_boundary is not None:
            self._unsub_boundary()
            self._unsub_boundary = None
        now = dt_util.utcnow()
        future = [
            race.start_time
            for races in data.races.values()
            for race in races
            if race.start_time is not None and race.start_time >= now
        ]
        if future:
            self._unsub_boundary = async_track_point_in_utc_time(
                self.hass,
                self._async_boundary_elapsed,
                min(future) + timedelta(seconds=1),
            )

    @callback
    def _async_boundary_elapsed(self, now: datetime) -> None:
        """Re-evaluate the next-race entities and arm the next known boundary."""
        self._unsub_boundary = None
        self.async_update_listeners()
        self._schedule_next_boundary(self.data)

    async def _async_update_data(self) -> ScheduleData:
        """Keep independent successful schedules when another series fails."""
        now = dt_util.utcnow()
        races = dict(self.data.races) if self.data else {}
        updated = dict(self.data.updated_at) if self.data else {}
        failed: set[int] = set()
        error: ProviderError | None = None
        self.last_error_status = None
        for series_id in self.series:
            try:
                current = await self.provider.async_get_schedule(now.year, series_id)
                # The next season is optional until published. Never discard the
                # current season merely because the next feed is not ready.
                if now.month >= 11:
                    try:
                        upcoming = await self.provider.async_get_schedule(
                            now.year + 1, series_id
                        )
                        current = (*current, *upcoming)
                    except ProviderError:
                        pass
                races[series_id] = tuple(
                    sorted(
                        current,
                        key=lambda race: (
                            race.start_time or datetime.max.replace(tzinfo=dt_util.UTC)
                        ),
                    )
                )
                updated[series_id] = now
            except ProviderError as err:
                failed.add(series_id)
                error = err
                self.last_error_status = err.status
        if len(failed) == len(self.series):
            raise UpdateFailed(f"Schedule provider unavailable: {error}") from error
        data = ScheduleData(
            races=races, failed_series=frozenset(failed), updated_at=updated
        )
        self._schedule_next_boundary(data)
        return data

    def next_race(self, series_id: int) -> Race | None:
        """Find the next timestamped race without assuming provider list order."""
        now = dt_util.utcnow()
        return next(
            (
                race
                for race in self.data.races.get(series_id, ())
                if race.start_time is not None and race.start_time >= now
            ),
            None,
        )


class LiveCoordinator(DataUpdateCoordinator[LiveSnapshot | None]):
    """Share one global live request across every selected series."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        provider: RaceProvider,
        schedule: ScheduleCoordinator,
        live_interval: int,
    ) -> None:
        """Use schedule proximity and source freshness to choose a prudent pace."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="NASCAR live feed",
            update_interval=LIVE_OFF_SEASON_INTERVAL,
        )
        self.provider = provider
        self.schedule = schedule
        self.live_interval = timedelta(seconds=live_interval)
        self.last_successful_update: datetime | None = None
        self.last_error_status: int | None = None
        self._unsub_source_expiry: Callable[[], None] | None = None

    async def async_shutdown(self) -> None:
        """Cancel source freshness updates as well as network polling."""
        if self._unsub_source_expiry is not None:
            self._unsub_source_expiry()
            self._unsub_source_expiry = None
        await super().async_shutdown()

    @callback
    def _schedule_source_expiry(self, snapshot: LiveSnapshot | None) -> None:
        """Expire source readings locally even when the provider poll is hours away."""
        if self._unsub_source_expiry is not None:
            self._unsub_source_expiry()
            self._unsub_source_expiry = None
        if snapshot is None or snapshot.source_updated_at is None:
            return
        now = dt_util.utcnow()
        if snapshot.source_updated_at > now + timedelta(minutes=5):
            return
        expires_at = (
            snapshot.source_updated_at + LIVE_STALE_AFTER + timedelta(seconds=1)
        )
        if expires_at > now:
            self._unsub_source_expiry = async_track_point_in_utc_time(
                self.hass, self._async_source_expired, expires_at
            )

    @callback
    def _async_source_expired(self, now: datetime) -> None:
        """Refresh entity health and availability without fetching the feed."""
        self._unsub_source_expiry = None
        self.async_update_listeners()

    @property
    def source_is_stale(self) -> bool | None:
        """Fresh HTTP responses do not imply that the source data is current."""
        if self.data is None or self.data.source_updated_at is None:
            return None
        age = dt_util.utcnow() - self.data.source_updated_at
        if age < -timedelta(minutes=5):
            return None
        return age > LIVE_STALE_AFTER

    def _next_interval(self, snapshot: LiveSnapshot | None) -> timedelta:
        """Use faster polling only for source-confirmed activity or a race window."""
        now = dt_util.utcnow()
        if (
            snapshot is not None
            and snapshot.series_id in self.schedule.series
            and snapshot.source_updated_at is not None
            and -timedelta(minutes=5)
            <= now - snapshot.source_updated_at
            <= LIVE_STALE_AFTER
            and snapshot.flag != "checkered"
            and snapshot.lap is not None
            and snapshot.lap > 0
        ):
            return self.live_interval
        interval = max(self.live_interval, LIVE_OFF_SEASON_INTERVAL)
        for races in self.schedule.data.races.values():
            for race in races:
                if race.start_time is None:
                    continue
                delta = race.start_time - now
                if -timedelta(hours=8) <= delta <= timedelta(hours=2):
                    interval = min(
                        interval, max(self.live_interval, timedelta(minutes=15))
                    )
                elif timedelta(0) <= delta <= timedelta(days=2):
                    interval = min(
                        interval, max(self.live_interval, LIVE_IDLE_INTERVAL)
                    )
        return interval

    async def _async_update_data(self) -> LiveSnapshot | None:
        """Failure of this optional feed never stops schedule entities."""
        try:
            snapshot = await self.provider.async_get_live()
        except ProviderError as err:
            self.last_error_status = err.status
            self.update_interval = max(
                self._next_interval(self.data), timedelta(seconds=err.retry_after or 0)
            )
            raise UpdateFailed(f"Live provider unavailable: {err}") from err
        self.last_error_status = None
        self.last_successful_update = dt_util.utcnow()
        self.update_interval = self._next_interval(snapshot)
        self._schedule_source_expiry(snapshot)
        return snapshot
