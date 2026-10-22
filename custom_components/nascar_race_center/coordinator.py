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

from .api import NascarApiClient
from .const import (
    LIVE_OFF_SEASON_INTERVAL,
    LIVE_STALE_AFTER,
    SCHEDULE_INTERVAL,
    SCHEDULE_STALE_AFTER,
)
from .endpoints import LIVE_FEED
from .live_view import FeedHealth, LiveView
from .models import LiveSnapshot, PollingDeferred, ProviderError, Race
from .polling import (
    CONSERVATIVE_LIMITS,
    PollDecision,
    PollingLimits,
    adaptive_decision,
    legacy_decision,
)
from .provider import CFProvider, RaceProvider

_LOGGER = logging.getLogger(__name__)


def _observations(snapshot: LiveSnapshot) -> tuple[object, ...]:
    """Compare reported activity without mistaking clock/name/car edits for racing."""
    board = snapshot.leaderboard
    drivers = (
        tuple(
            (
                row.driver_id,
                row.position,
                row.laps_completed,
                row.last_lap_time,
                row.best_lap_time,
                row.last_lap_speed,
                row.best_lap_speed,
                row.average_speed,
                row.gap,
                row.status_code,
                row.is_on_track,
                row.pit_stops,
                row.laps_led,
            )
            for row in board.drivers
        )
        if board is not None
        else None
    )
    return snapshot.lap, snapshot.flag, snapshot.stage, drivers


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
        *,
        polling_policy: str = "conservative",
        approaching_interval: int = 60,
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
        self.polling_policy = polling_policy
        self.approaching_interval = approaching_interval
        limits = getattr(provider, "polling_limits", None)
        self.polling_limits = (
            limits if isinstance(limits, PollingLimits) else CONSERVATIVE_LIMITS
        )
        self.poll_decision = PollDecision(21600, "startup")
        self.interval_constraint: str | None = None
        self._failure_count = 0
        self._stale_reads = 0
        self._source_high_water: datetime | None = None
        self._clock_regressed = False
        self._has_read = False
        self.observation_state = "not_observed"
        self._observed_context: tuple[int, int, int | None] | None = None
        self._unsub_schedule = schedule.async_add_listener(self._schedule_changed)
        self.last_successful_update: datetime | None = None
        self.last_error_status: int | None = None
        self._unsub_source_expiry: Callable[[], None] | None = None
        self._stopped = False

    async def async_shutdown(self) -> None:
        """Cancel source freshness updates as well as network polling."""
        self._stopped = True
        self._unsub_schedule()
        if self._unsub_source_expiry is not None:
            self._unsub_source_expiry()
            self._unsub_source_expiry = None
        await super().async_shutdown()

    @callback
    def _schedule_changed(self) -> None:
        """Re-arm the same HA poll after schedule revisions, without requesting data."""
        if self._stopped or not self._has_read or not self.last_update_success:
            return
        self.update_interval = self._next_interval(self.data)
        self.async_set_updated_data(self.data)

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
        elif self.source_is_stale:
            health = "stale"
        else:
            health = "freshness_unknown" if self._clock_regressed else "ok"
        return LiveView(
            snapshot if matching else None,
            health,
            self.observation_state
            if isinstance(self.provider, CFProvider)
            and matching
            and snapshot is not None
            and snapshot.session_key == self._observed_context
            else None,
        )

    def _next_interval(self, snapshot: LiveSnapshot | None) -> timedelta:
        """One scheduling owner applies evidence, provider, cache and failure limits."""
        now = dt_util.utcnow()
        selected = (
            snapshot
            if snapshot and snapshot.series_id in self.schedule.series
            else None
        )
        if (
            isinstance(self.provider, CFProvider)
            and selected is not None
            and (
                self._clock_regressed
                or not LiveView(selected, "ok", self.observation_state).available
                or selected.leaderboard is None
            )
        ):
            selected = None
        known_series = {
            series
            for series in self.schedule.series
            if self.schedule.last_update_success
            and series not in self.schedule.data.failed_series
            and (updated := self.schedule.data.updated_at.get(series)) is not None
            and timedelta(0) <= now - updated <= SCHEDULE_STALE_AFTER
        }
        races = tuple(
            race
            for series in known_series
            for race in self.schedule.usable_races(series)
            if race.series_id == series
        )
        adaptive = self.polling_policy == "adaptive" and self.polling_limits.adaptive
        decision = (
            adaptive_decision(
                selected
                if not self._clock_regressed and not self._failure_count
                else None,
                races,
                now,
                schedules_known=len(known_series) == len(self.schedule.series),
                approaching_seconds=self.approaching_interval,
            )
            if adaptive
            else legacy_decision(
                selected, races, now, int(self.live_interval.total_seconds())
            )
        )
        self.poll_decision = decision
        if adaptive and self._failure_count and selected is not None:
            # A transient live outage must not turn the next retry into an
            # off-season six-hour wait. It cannot establish current activity.
            decision = PollDecision(min(decision.seconds, 300), "conservative_fallback")
            self.poll_decision = decision
        seconds = max(decision.seconds, self.polling_limits.minimum_seconds)
        self.interval_constraint = (
            "provider_policy"
            if self.polling_policy == "adaptive" and not adaptive
            else None
        )
        if self._clock_regressed or self._stale_reads:
            seconds = max(
                seconds, min(3600, 300 * 2 ** min(max(0, self._stale_reads - 1), 4))
            )
            self.interval_constraint = "source_not_advancing"
        if self._failure_count:
            seconds = max(seconds, min(3600, 60 * 2 ** min(self._failure_count - 1, 6)))
            self.interval_constraint = "failure_backoff"
        api = getattr(self.provider, "api", None)
        if isinstance(api, NascarApiClient):
            delay = api.request_delay(LIVE_FEED)
            if delay > seconds:
                seconds = delay
                self.interval_constraint = "cache_or_cooldown"
        # Cache and transport retain their full deadline. Bound HA's timer
        # arithmetic; an earlier local wake only reads that still-fresh cache.
        return timedelta(seconds=min(seconds, 366 * 86400))

    def polling_diagnostics(self) -> dict[str, object]:
        """Small current decisions only; no timeline or source payload retention."""
        now = dt_util.utcnow()
        clock = self.data.source_updated_at if self.data else None
        api = getattr(self.provider, "api", None)
        return {
            "configured_policy": self.polling_policy,
            "provider_policy": self.polling_limits.name,
            "fast_permitted": self.polling_limits.fast_permitted,
            "conservative_minimum_seconds": self.live_interval.total_seconds(),
            "approaching_seconds": self.approaching_interval,
            "target_interval_seconds": self.poll_decision.seconds,
            "effective_interval_seconds": self.update_interval.total_seconds()
            if self.update_interval
            else None,
            "reason": self.poll_decision.reason,
            "constraint": self.interval_constraint,
            "source_content_age_seconds": (now - clock).total_seconds()
            if clock
            else None,
            "consecutive_failures": self._failure_count,
            "nonadvancing_reads": self._stale_reads,
            "observation_advancement": self.observation_state,
            "source_clock_regressed": self._clock_regressed,
            "network_eligible_in_seconds": api.request_delay(LIVE_FEED)
            if isinstance(api, NascarApiClient)
            else None,
        }

    async def _async_update_data(self) -> LiveSnapshot | None:
        """Failure of this optional feed never stops schedule entities."""
        try:
            snapshot = await self.provider.async_get_live()
        except ProviderError as err:
            self.last_error_status = err.status
            if isinstance(err, PollingDeferred):
                self.interval_constraint = "restart_reservation"
                self.update_interval = timedelta(
                    seconds=max(
                        self.polling_limits.minimum_seconds, err.retry_after or 0
                    )
                )
                raise UpdateFailed("Live request slot is reserved") from err
            self._failure_count = min(7, self._failure_count + 1)
            self.update_interval = max(
                self._next_interval(self.data), timedelta(seconds=err.retry_after or 0)
            )
            raise UpdateFailed(f"Live provider unavailable: {err}") from err
        self.last_error_status = None
        self._has_read = True
        self._failure_count = 0
        previous = self.data
        context = snapshot.session_key if snapshot else None
        if context != self._observed_context:
            self._stale_reads = 0
        if snapshot is None:
            self.observation_state = "no_session"
        elif (
            previous is None
            or previous.session_key != context
            or previous.run_type_code != snapshot.run_type_code
        ):
            self.observation_state = "first_observation"
        elif (
            isinstance(self.provider, CFProvider)
            and self.provider.api.diagnostics().get(LIVE_FEED, {}).get("delivery")
            == "cache"
        ):
            # A local consumer read supplies no new evidence about the source.
            # Retain the assessment until a network observation or local expiry.
            pass
        elif snapshot.source_updated_at == previous.source_updated_at:
            self.observation_state = "clock_unchanged"
        elif _observations(snapshot) == _observations(previous):
            self.observation_state = "timestamp_only"
        else:
            self.observation_state = "observations_changed"
        self._observed_context = context
        clock = snapshot.source_updated_at if snapshot else None
        now = dt_util.utcnow()
        if (
            clock is not None
            and clock <= now
            and (self._source_high_water is None or clock > self._source_high_water)
        ):
            self._source_high_water = clock
            self._stale_reads = 0
            self._clock_regressed = False
        else:
            self._clock_regressed = clock is not None and (
                clock > now
                or self._source_high_water is not None
                and clock < self._source_high_water
            )
        if snapshot is not None and (
            clock is None
            or now - clock >= timedelta(seconds=60)
            or self._clock_regressed
        ):
            self._stale_reads = min(5, self._stale_reads + 1)
        self.last_successful_update = dt_util.utcnow()
        self.update_interval = self._next_interval(snapshot)
        self._schedule_source_expiry(snapshot)
        return snapshot
