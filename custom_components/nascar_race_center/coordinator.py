"""Independent schedule and live update loops with bounded polling."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
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
from .live_view import FeedHealth, LiveView
from .models import LiveSnapshot, ProviderError, Race
from .provider import RaceProvider

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScheduleData:
    """Schedules and per-series freshness; never substitute failed data with zero."""

    races: dict[int, tuple[Race, ...]]
    failed_series: frozenset[int]
    updated_at: dict[int, datetime]
    failed_seasons: dict[int, frozenset[int]] = field(default_factory=dict)


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
        self._stopped = False

    async def async_shutdown(self) -> None:
        """Release the local race-boundary timer along with provider polling."""
        self._stopped = True
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
            for series_id, races in data.races.items()
            for race in races
            if race.start_time is not None
            and series_id not in data.failed_series
            and (race.season or now.year)
            not in data.failed_seasons.get(series_id, frozenset())
            and now
            <= race.start_time
            <= datetime.max.replace(tzinfo=dt_util.UTC) - timedelta(seconds=1)
        ]
        if future and not self._stopped:
            self._unsub_boundary = async_track_point_in_utc_time(
                self.hass,
                self._async_boundary_elapsed,
                min(future) + timedelta(seconds=1),
            )

    @callback
    def _async_boundary_elapsed(self, now: datetime) -> None:
        """Re-evaluate the next-race entities and arm the next known boundary."""
        self._unsub_boundary = None
        if self._stopped:
            return
        self.async_update_listeners()
        self._schedule_next_boundary(self.data)

    async def _async_update_data(self) -> ScheduleData:
        """Keep usable seasons independent, retaining failed ones for diagnostics."""
        now = dt_util.utcnow()
        races = dict(self.data.races) if self.data else {}
        updated = dict(self.data.updated_at) if self.data else {}
        failed: set[int] = set()
        failed_seasons: dict[int, frozenset[int]] = {}
        error: ProviderError | None = None
        self.last_error_status = None
        for series_id in self.series:
            previous = races.get(series_id, ())
            # Source adapters supply seasons. Preserve Phase 1/custom-provider
            # models without one by treating them as the requested current year.
            season_rows = {
                season: tuple(
                    race
                    for race in previous
                    if (race.season or now.year) == season
                    and (season >= now.year or self._has_remaining_time(race, now))
                )
                for season in range(
                    max(1948, now.year - 1), min(9999, now.year + 1) + 1
                )
            }
            years = [now.year]
            if now.month >= 11 and now.year < 9999:
                years.append(now.year + 1)
            # Discover cross-year weekends after a restart in January. Continue
            # refreshing an observed postponed weekend until its known times end.
            if now.year > 1948 and (now.month == 1 or season_rows.get(now.year - 1)):
                years.append(now.year - 1)
            successful: set[int] = set()
            failed_years: set[int] = set()
            for year in years:
                try:
                    rows = await self.provider.async_get_schedule(year, series_id)
                    season_rows[year] = (
                        tuple(
                            race for race in rows if self._has_remaining_time(race, now)
                        )
                        if year < now.year
                        else rows
                    )
                    successful.add(year)
                except ProviderError as err:
                    failed_years.add(year)
                    error = err
                    self.last_error_status = err.status
            failed_seasons[series_id] = frozenset(failed_years)
            # A valid empty current season is meaningful. An empty optional
            # season cannot conceal failure of the requested current schedule.
            usable = now.year in successful or any(
                season_rows[year] for year in successful
            )
            if not usable:
                failed.add(series_id)
            else:
                updated[series_id] = now
            unique = {
                (race.series_id, race.season or year, race.race_id): race
                for year, rows in season_rows.items()
                for race in rows
            }
            races[series_id] = tuple(
                sorted(
                    unique.values(),
                    key=lambda race: (
                        race.start_time or datetime.max.replace(tzinfo=dt_util.UTC)
                    ),
                )
            )
        if len(failed) == len(self.series):
            raise UpdateFailed(f"Schedule provider unavailable: {error}") from error
        data = ScheduleData(
            races=races,
            failed_series=frozenset(failed),
            updated_at=updated,
            failed_seasons=failed_seasons,
        )
        self._schedule_next_boundary(data)
        return data

    @staticmethod
    def _has_remaining_time(race: Race, now: datetime) -> bool:
        """Retain only known future/ongoing prior-season dates, never guess."""
        return (race.start_time is not None and race.start_time >= now) or any(
            boundary >= now
            for session in race.sessions
            if (boundary := session.end_time or session.start_time) is not None
        )

    def usable_races(self, series_id: int) -> tuple[Race, ...]:
        """Exclude failed retained seasons from entities and polling decisions."""
        if not self.last_update_success or series_id in self.data.failed_series:
            return ()
        failed = self.data.failed_seasons.get(series_id, frozenset())
        year = dt_util.utcnow().year
        return tuple(
            race
            for race in self.data.races.get(series_id, ())
            if (race.season or year) not in failed
        )

    def next_race(self, series_id: int) -> Race | None:
        """Find the next timestamped race without assuming provider list order."""
        now = dt_util.utcnow()
        return next(
            (
                race
                for race in self.usable_races(series_id)
                if race.start_time is not None
                and race.start_time >= now
                and race.status not in {"canceled", "cancelled"}
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
        self._stopped = False

    async def async_shutdown(self) -> None:
        """Cancel source freshness updates as well as network polling."""
        self._stopped = True
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
        if self._stopped or snapshot is None or snapshot.source_updated_at is None:
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
        if self._stopped:
            return
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

    def view(self, series_id: int) -> LiveView:
        """Provide one series' health and scoring without duplicating global data."""
        snapshot = self.data
        matching = (
            snapshot is not None
            and snapshot.series_id == series_id
            and series_id in self.schedule.series
        )
        health: FeedHealth
        if not self.last_update_success:
            health = "denied" if self.last_error_status in {401, 403} else "offline"
        elif snapshot is None:
            health = "no_active_session"
        elif not matching:
            health = "not_reported"
        elif self.source_is_stale is None:
            health = "freshness_unknown"
        else:
            health = "stale" if self.source_is_stale else "ok"
        return LiveView(snapshot if matching else None, health)

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
            and snapshot.flag in {"green", "yellow", "red", "white"}
            and snapshot.lap is not None
            and snapshot.lap > 0
        ):
            return self.live_interval
        interval = max(self.live_interval, LIVE_OFF_SEASON_INTERVAL)
        for series_id in self.schedule.series:
            for race in self.schedule.usable_races(series_id):
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
