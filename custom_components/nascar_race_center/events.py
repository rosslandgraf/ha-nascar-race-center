"""Conservative typed transitions over normalized observations, without HA actions.

The durable ledger contains clocks, progress and hashes, never racing feeds.
Callers must persist export() successfully BEFORE publishing returned events.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from typing import Any

from .const import LIVE_STALE_AFTER
from .models import LiveSnapshot, Race
from .scoring import latest_pit

EVENT_NAMESPACE = "nascar_race_center_event"
MAX_SESSIONS = 64
MAX_EVENT_IDS = 2048
MAX_REMINDERS = 300


class EventType(StrEnum):
    """Stable public event types; unsupported racing semantics are absent."""

    UPCOMING = "upcoming_race"
    STARTED = "session_started"
    FLAG = "flag_changed"
    LEAD = "lead_changed"
    FAVORITE_LEAD = "favorite_lead"
    TOP_ENTER = "favorite_top_n_entered"
    TOP_LEAVE = "favorite_top_n_left"
    PIT = "favorite_pit_observed"


GENERAL_EVENTS = tuple(EventType)[:4]
FAVORITE_EVENTS = tuple(EventType)[4:]


@dataclass(frozen=True, slots=True)
class EventPreferences:
    """Every event is opt-in; absent legacy options stay disabled."""

    enabled: bool = False
    types: frozenset[EventType] = frozenset()
    favorites: frozenset[int] = frozenset()
    top_n: int = 10
    reminder_minutes: int = 30

    @classmethod
    def from_options(
        cls, options: dict[str, Any], favorites: tuple[int, ...]
    ) -> EventPreferences:
        """Validate persisted options as strictly as the UI."""
        enabled = options.get("racing_events", False)
        top_n = options.get("event_top_n", 10)
        minutes = options.get("reminder_minutes", 30)
        if (
            not isinstance(enabled, bool)
            or type(top_n) is not int
            or not 1 <= top_n <= 40
            or type(minutes) is not int
            or not 1 <= minutes <= 1440
        ):
            raise ValueError("Invalid racing event settings")
        selected: set[EventType] = set()
        for key, allowed in (
            ("event_types", GENERAL_EVENTS),
            ("favorite_event_types", FAVORITE_EVENTS),
        ):
            values = options.get(key, [])
            if not isinstance(values, list) or any(
                value not in allowed for value in values
            ):
                raise ValueError("Invalid event preference")
            selected.update(EventType(value) for value in values)
        return cls(enabled, frozenset(selected), frozenset(favorites), top_n, minutes)


@dataclass(frozen=True, slots=True)
class RacingEvent:
    """Small immutable public contract, independent of provider dictionaries."""

    event_type: EventType
    event_id: str
    series_id: int
    race_id: int
    run_id: int | None
    driver_id: int | None
    source: str
    source_time: datetime
    detail: tuple[tuple[str, str | int], ...] = ()

    def payload(self) -> dict[str, str | int | None]:
        """JSON-safe attributes with IDs instead of names or full field data."""
        return {
            "event_type": self.event_type.value,
            "event_id": self.event_id,
            "series_id": self.series_id,
            "race_id": self.race_id,
            "run_id": self.run_id,
            "driver_id": self.driver_id,
            "source": self.source,
            "source_time": self.source_time.isoformat(),
            **dict(self.detail),
        }


@dataclass(frozen=True, slots=True)
class SessionMark:
    time: datetime
    lap: int
    elapsed: int | None
    started: bool
    completed: bool


class EventEngine:
    """One global baseline with bounded persistent replay barriers.

    Failed observations, switching sessions and gaps invalidate continuity.
    High-water marks survive those baselines and option changes. Events favor
    omission over catch-up; this is at-most-once delivery, not a durable outbox.
    """

    def __init__(self, preferences: EventPreferences, source: str) -> None:
        self.preferences = preferences
        self.source = source
        self._previous: LiveSnapshot | None = None
        self._sessions: dict[str, SessionMark] = {}
        self._ids: dict[str, None] = {}
        self._floor: datetime | None = None
        self._reminded: dict[str, str] = {}
        self._reminder_floor: datetime | None = None
        self._reminders: dict[str, tuple[Race, datetime]] = {}
        self._schedule_time: datetime | None = None

    def invalidate(self) -> None:
        """Loss of evidence always requires a fresh silent baseline."""
        self._previous = None

    def export(self) -> dict[str, Any]:
        """Bounded versioned persistence; no names, vehicles or pit records."""
        return {
            "schema": 1,
            "floor": self._floor.isoformat() if self._floor else None,
            "sessions": {
                key: {
                    "time": mark.time.isoformat(),
                    "lap": mark.lap,
                    "elapsed": mark.elapsed,
                    "started": mark.started,
                    "completed": mark.completed,
                }
                for key, mark in self._sessions.items()
            },
            "ids": list(self._ids),
            "reminded": dict(self._reminded),
            "reminder_floor": self._reminder_floor.isoformat()
            if self._reminder_floor
            else None,
        }

    def restore(self, data: dict[str, Any]) -> None:
        """Reject corrupt/future storage rather than silently losing protection."""
        if (
            not isinstance(data, dict)
            or data.get("schema") != 1
            or not isinstance(data.get("sessions"), dict)
            or len(data["sessions"]) > MAX_SESSIONS
            or not isinstance(data.get("ids"), list)
            or len(data["ids"]) > MAX_EVENT_IDS
            or not isinstance(data.get("reminded", {}), dict)
            or len(data.get("reminded", {})) > MAX_REMINDERS
        ):
            raise ValueError("Invalid event ledger")
        sessions: dict[str, SessionMark] = {}
        for key, row in data["sessions"].items():
            if not isinstance(key, str) or len(key) > 120 or not isinstance(row, dict):
                raise ValueError("Invalid session ledger")
            time = _clock(row.get("time"))
            lap, elapsed = row.get("lap"), row.get("elapsed")
            if (
                type(lap) is not int
                or lap < 0
                or elapsed is not None
                and (type(elapsed) is not int or elapsed < 0)
                or type(row.get("started")) is not bool
                or type(row.get("completed")) is not bool
            ):
                raise ValueError("Invalid session progress")
            sessions[key] = SessionMark(
                time, lap, elapsed, row["started"], row["completed"]
            )
        ids = data["ids"]
        if any(not isinstance(value, str) or len(value) != 64 for value in ids):
            raise ValueError("Invalid event IDs")
        self._floor = _clock(data["floor"]) if data.get("floor") else None
        reminded = data.get("reminded", {})
        for key, value in reminded.items():
            if not isinstance(key, str) or len(key) > 120:
                raise ValueError("Invalid reminder identity")
            _clock(value)
        self._reminded = dict(reminded)
        self._reminder_floor = (
            _clock(data["reminder_floor"]) if data.get("reminder_floor") else None
        )
        self._sessions = sessions
        self._ids = dict.fromkeys(ids)
        self.invalidate()

    def _event(
        self,
        kind: EventType,
        series: int,
        race: int,
        run: int | None,
        time: datetime,
        discriminator: str,
        driver: int | None = None,
        **detail: str | int,
    ) -> RacingEvent | None:
        if not self.preferences.enabled or kind not in self.preferences.types:
            return None
        identity = (
            f"v1:{self.source}:{series}:{race}:{run}:{kind}:{driver}:{discriminator}"
        )
        event_id = sha256(identity.encode()).hexdigest()
        if event_id in self._ids:
            return None
        self._ids[event_id] = None
        while len(self._ids) > MAX_EVENT_IDS:
            del self._ids[next(iter(self._ids))]
        return RacingEvent(
            kind,
            event_id,
            series,
            race,
            run,
            driver,
            self.source,
            time,
            tuple(sorted(detail.items())),
        )

    def observe(
        self,
        snapshot: LiveSnapshot | None,
        *,
        valid: bool,
        now: datetime,
    ) -> tuple[RacingEvent, ...]:
        """Compare only successive valid, advancing observations of one race run."""
        if (
            not self.preferences.enabled
            or not valid
            or snapshot is None
            or snapshot.status != "race"
            or snapshot.run_id is None
            or snapshot.race_id <= 0
            or snapshot.run_id <= 0
            or snapshot.source_updated_at is None
            or snapshot.lap is None
            or snapshot.flag
            not in {
                "cold_track",
                "hot_track",
                "green",
                "yellow",
                "red",
                "white",
                "checkered",
            }
            or not timedelta(0) <= now - snapshot.source_updated_at <= LIVE_STALE_AFTER
        ):
            self.invalidate()
            return ()
        time = snapshot.source_updated_at
        key = f"{self.source}:{snapshot.series_id}:{snapshot.race_id}:{snapshot.run_id}"
        mark = self._sessions.get(key)
        if (
            self._floor is not None
            and time <= self._floor
            or mark is not None
            and (
                time <= mark.time
                or snapshot.lap < mark.lap
                or mark.elapsed is not None
                and snapshot.elapsed_seconds is not None
                and snapshot.elapsed_seconds < mark.elapsed
            )
        ):
            # Identical cached observations keep continuity. Conflicting or
            # regressing samples break it, even when they carry a newer clock.
            if snapshot != self._previous:
                self.invalidate()
            return ()
        previous = self._previous
        self._previous = snapshot
        active = (
            snapshot.flag in {"green", "yellow", "red", "white"} and snapshot.lap > 0
        )
        completed = snapshot.flag == "checkered"
        self._sessions.pop(key, None)
        self._sessions[key] = SessionMark(
            time,
            snapshot.lap,
            snapshot.elapsed_seconds
            if snapshot.elapsed_seconds is not None
            else mark.elapsed
            if mark
            else None,
            active or bool(mark and mark.started),
            completed or bool(mark and mark.completed),
        )
        while len(self._sessions) > MAX_SESSIONS:
            removed = self._sessions.pop(next(iter(self._sessions)))
            self._floor = max(self._floor or removed.time, removed.time)
        if (
            previous is None
            or previous.session_key != snapshot.session_key
            or previous.source_updated_at is None
            or time - previous.source_updated_at > LIVE_STALE_AFTER
            or mark is not None
            and mark.completed
        ):
            return ()
        events: list[RacingEvent] = []

        def emit(
            kind: EventType,
            discriminator: str | None = None,
            driver: int | None = None,
            **detail: str | int,
        ) -> None:
            event = self._event(
                kind,
                snapshot.series_id,
                snapshot.race_id,
                snapshot.run_id,
                time,
                discriminator or time.isoformat(),
                driver,
                **detail,
            )
            if event is not None:
                events.append(event)

        if (
            active
            and snapshot.flag == "green"
            and previous.lap == 0
            and previous.flag in {"cold_track", "hot_track", "green"}
            and not (mark and mark.started)
        ):
            emit(EventType.STARTED, "start", lap=snapshot.lap)
        if previous.flag != snapshot.flag and snapshot.flag in {
            "green",
            "yellow",
            "red",
            "white",
            "checkered",
        }:
            emit(
                EventType.FLAG,
                "checkered" if completed else None,
                flag=snapshot.flag,
                lap=snapshot.lap,
                completion="observed" if completed else "unknown",
            )
        # Checkered is one flag observation, never an additional finish/result event.
        if completed or not active:
            return tuple(events)
        before, after = previous.leaderboard, snapshot.leaderboard
        if (
            before is None
            or after is None
            or previous.leaderboard_failed
            or snapshot.leaderboard_failed
        ):
            return tuple(events)
        old_leader, leader = before.leader, after.leader
        if (
            old_leader is not None
            and leader is not None
            and old_leader.driver_id != leader.driver_id
            and leader.driver_id in before.by_driver
            and old_leader.driver_id in after.by_driver
        ):
            emit(
                EventType.LEAD,
                driver=leader.driver_id,
                previous_driver_id=old_leader.driver_id,
            )
            if leader.driver_id in self.preferences.favorites:
                emit(
                    EventType.FAVORITE_LEAD,
                    driver=leader.driver_id,
                    previous_driver_id=old_leader.driver_id,
                )
        old_ranks = Counter(driver.position for driver in before.drivers)
        ranks = Counter(driver.position for driver in after.drivers)
        for driver_id in sorted(self.preferences.favorites):
            old, driver = (
                before.by_driver.get(driver_id),
                after.by_driver.get(driver_id),
            )
            if old is None or driver is None:
                continue
            if (
                old.position is not None
                and driver.position is not None
                and old_ranks[old.position] == ranks[driver.position] == 1
                and (old.position <= self.preferences.top_n)
                != (driver.position <= self.preferences.top_n)
            ):
                emit(
                    EventType.TOP_ENTER
                    if driver.position <= self.preferences.top_n
                    else EventType.TOP_LEAVE,
                    driver=driver_id,
                    position=driver.position,
                    previous_position=old.position,
                    top_n=self.preferences.top_n,
                )
            if old.pits_failed or driver.pits_failed or old.pit_stops is None:
                continue
            stop = latest_pit(driver.pit_stops)
            prior = latest_pit(old.pit_stops)
            if (
                stop is not None
                and stop.lap is not None
                and stop.entry_time is not None
                and (
                    not old.pit_stops
                    or prior is not None
                    and prior.lap is not None
                    and stop.lap > prior.lap
                )
                and previous.lap is not None
                and previous.lap <= stop.lap <= snapshot.lap
            ):
                emit(
                    EventType.PIT,
                    f"pit:{stop.lap}:{stop.entry_time}",
                    driver_id,
                    pit_lap=stop.lap,
                )
        return tuple(events)

    def reminders(
        self, races: tuple[Race, ...], now: datetime
    ) -> tuple[RacingEvent, ...]:
        """Only cross an already watched, unchanged future schedule deadline.

        Setup inside a reminder window, rescheduling, outages and long clock jumps
        never backfill reminders. The caller supplies only healthy usable races.
        """
        pending: dict[str, tuple[Race, datetime]] = {}
        events: list[RacingEvent] = []
        for race in races[:MAX_REMINDERS]:
            start = race.start_time
            if (
                start is None
                or start <= now
                or race.status in {"cancelled", "canceled"}
            ):
                continue
            key = f"{self.source}:{race.series_id}:{race.season}:{race.race_id}"
            deadline = start - timedelta(minutes=self.preferences.reminder_minutes)
            if (
                key in self._reminded
                or self._reminder_floor is not None
                and deadline <= self._reminder_floor
            ):
                continue
            old = self._reminders.get(key)
            if (
                old is not None
                and old[0].start_time == start
                and self._schedule_time is not None
                and self._schedule_time < deadline <= now
                and now - deadline <= timedelta(minutes=1)
            ):
                event = self._event(
                    EventType.UPCOMING,
                    race.series_id,
                    race.race_id,
                    None,
                    now,
                    f"{race.season}",
                    scheduled_start=start.isoformat(),
                    reminder_minutes=self.preferences.reminder_minutes,
                )
                if event is not None:
                    events.append(event)
                    self._reminded[key] = deadline.isoformat()
                    while len(self._reminded) > MAX_REMINDERS:
                        removed = _clock(self._reminded.pop(next(iter(self._reminded))))
                        self._reminder_floor = max(
                            self._reminder_floor or removed, removed
                        )
            pending[key] = (race, deadline)
        self._reminders = pending
        self._schedule_time = now
        return tuple(events)

    def next_reminder(self, now: datetime) -> datetime | None:
        """A single local timer suffices; reminders never poll NASCAR."""
        if (
            not self.preferences.enabled
            or EventType.UPCOMING not in self.preferences.types
        ):
            return None
        return min(
            (deadline for _, deadline in self._reminders.values() if deadline > now),
            default=None,
        )


def _clock(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Missing ledger clock")
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("Ambiguous ledger clock")
    return result
