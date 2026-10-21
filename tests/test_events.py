"""Replay synthetic normalized observations, never real NASCAR data."""

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from custom_components.nascar_race_center.events import (
    MAX_EVENT_IDS,
    MAX_SESSIONS,
    EventEngine,
    EventPreferences,
    EventType,
)
from custom_components.nascar_race_center.models import LiveSnapshot, Race
from custom_components.nascar_race_center.scoring import PitStop
from custom_components.nascar_race_center.timing import Leaderboard, LiveDriver

BASE = datetime(2026, 10, 21, 16, tzinfo=UTC)
PREFS = EventPreferences(True, frozenset(EventType), frozenset({99001}), 10, 30)


def sample(second: int, *, position: int = 12, pit: int | None = None, **changes):
    """One current field; identity always comes from NASCAR IDs."""
    drivers = (
        LiveDriver(
            99001,
            position=position,
            pit_stops=(PitStop(lap=pit, entry_time=20.0),) if pit else (),
        ),
        LiveDriver(99002, position=2 if position == 1 else 1, pit_stops=()),
    )
    return replace(
        LiveSnapshot(
            1,
            9001,
            status="race",
            flag="green",
            lap=second // 30 + 1,
            run_id=8,
            source_updated_at=BASE + timedelta(seconds=second),
            leaderboard=Leaderboard(drivers, 2),
        ),
        **changes,
    )


def observe(engine, snapshot, *, valid=True, now=None):
    return engine.observe(snapshot, valid=valid, now=now or snapshot.source_updated_at)


def kinds(events):
    return [event.event_type for event in events]


def test_full_replay_and_unchanged_refreshes():
    engine = EventEngine(PREFS, "synthetic")
    events = []
    frames = json.loads(
        (Path(__file__).parent / "fixtures/phase3c/race_sequence.json").read_text()
    )
    for frame in frames:
        snapshot = sample(
            frame["second"],
            position=frame["favorite_position"],
            pit=frame.get("pit_lap"),
            lap=frame["lap"],
            flag=frame["flag"],
        )
        batch = observe(engine, snapshot)
        events.extend(batch)
        for _ in range(5):
            assert observe(engine, snapshot) == ()
    assert kinds(events).count(EventType.STARTED) == 1
    assert kinds(events).count(EventType.FAVORITE_LEAD) == 1
    assert kinds(events).count(EventType.TOP_ENTER) == 1
    assert kinds(events).count(EventType.TOP_LEAVE) == 1
    assert kinds(events).count(EventType.PIT) == 1
    flags = [
        event.payload()["flag"]
        for event in events
        if event.event_type == EventType.FLAG
    ]
    assert flags == ["green", "yellow", "green", "red", "green", "white", "checkered"]
    checkered = [
        event for event in events if event.payload().get("flag") == "checkered"
    ]
    assert len(checkered) == 1
    assert checkered[0].payload()["completion"] == "observed"
    assert len({event.event_id for event in events}) == len(events)
    assert "official" not in json.dumps([event.payload() for event in events])
    assert observe(engine, sample(240, flag="green")) == ()
    assert observe(engine, sample(270, flag="checkered")) == ()


@pytest.mark.parametrize(
    "flag", ["green", "yellow", "red", "white", "checkered", "cold_track"]
)
def test_initial_observation_is_always_silent(flag):
    engine = EventEngine(PREFS, "synthetic")
    assert observe(engine, sample(0, position=1, pit=1, flag=flag)) == ()


@pytest.mark.parametrize(
    "changes",
    [
        {"source_updated_at": None},
        {"run_id": None},
        {"flag": None},
        {"lap": None},
        {"status": "practice"},
        {"status": "qualifying"},
        {"source_updated_at": BASE - timedelta(hours=1)},
        {"source_updated_at": BASE + timedelta(hours=1)},
    ],
)
def test_invalid_evidence_and_recovery_baseline(changes):
    engine = EventEngine(PREFS, "synthetic")
    assert observe(engine, sample(0)) == ()
    assert (
        observe(
            engine,
            sample(30, position=1, **{"flag": "yellow", **changes}),
            now=BASE + timedelta(seconds=30),
        )
        == ()
    )
    assert observe(engine, sample(60, position=1, flag="yellow")) == ()
    assert kinds(observe(engine, sample(90, flag="red"))) == [
        EventType.FLAG,
        EventType.LEAD,
        EventType.TOP_LEAVE,
    ]


def test_unavailable_reconnect_and_missing_source_never_catch_up():
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(0))
    assert observe(engine, sample(30, position=1), valid=False) == ()
    assert engine.observe(None, valid=True, now=BASE + timedelta(seconds=40)) == ()
    assert observe(engine, sample(60, position=1, flag="yellow")) == ()
    assert observe(engine, sample(60, position=1, flag="yellow")) == ()


@pytest.mark.parametrize(
    "changes", [{"race_id": 9002}, {"run_id": 9}, {"series_id": 2}, {"series_id": 3}]
)
def test_switch_and_return_to_previous_session_rebaseline(changes):
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(0))
    assert observe(engine, sample(30, position=1, flag="yellow", **changes)) == ()
    assert observe(engine, sample(60, position=1, flag="red")) == ()
    assert observe(engine, sample(0)) == ()  # replay below durable high-water
    assert observe(engine, sample(90, position=1, flag="green")) == ()


def test_missed_intervals_report_only_current_change_and_long_gaps_rebaseline():
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(0))
    events = observe(engine, sample(180, position=9, flag="yellow"))
    assert kinds(events) == [EventType.FLAG, EventType.TOP_ENTER]
    assert observe(engine, sample(1200, position=1, flag="red")) == ()
    assert observe(engine, sample(1230, position=1, flag="red")) == ()


@pytest.mark.parametrize(
    "missing", ["driver", "position", "leaderboard", "duplicate_rank"]
)
def test_missing_and_ambiguous_drivers_reappear_without_top_entry(missing):
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(0))
    snapshot = sample(30)
    if missing == "driver":
        snapshot = replace(
            snapshot, leaderboard=Leaderboard((LiveDriver(99002, position=1),), 1)
        )
    elif missing == "position":
        snapshot = sample(30, position=None)
    elif missing == "duplicate_rank":
        snapshot = replace(
            snapshot,
            leaderboard=Leaderboard(
                (LiveDriver(99001, position=12), LiveDriver(99002, position=12)), 2
            ),
        )
    else:
        snapshot = replace(snapshot, leaderboard=None)
    assert observe(engine, snapshot) == ()
    assert EventType.TOP_ENTER not in kinds(observe(engine, sample(60, position=9)))


def test_reordering_field_never_changes_leader_or_position():
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(0))
    snapshot = sample(30)
    assert (
        observe(
            engine,
            replace(
                snapshot,
                leaderboard=Leaderboard(
                    tuple(reversed(snapshot.leaderboard.drivers)), 2
                ),
            ),
        )
        == ()
    )


@pytest.mark.parametrize(
    "pit_changes",
    [
        {"entry_time": None},
        {"lap": None},
        {"lap": 1},
    ],
)
def test_incomplete_or_historical_pits_do_not_emit(pit_changes):
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(60))
    stop = replace(PitStop(lap=4, entry_time=12.0), **pit_changes)
    snapshot = sample(90)
    driver = replace(snapshot.leaderboard.drivers[0], pit_stops=(stop,))
    board = Leaderboard((driver, snapshot.leaderboard.drivers[1]), 2)
    assert observe(engine, replace(snapshot, leaderboard=board)) == ()


def test_pit_entry_then_exit_and_replay_are_one_observation():
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(0))
    assert kinds(observe(engine, sample(30, pit=2))) == [EventType.PIT]
    snapshot = sample(60, pit=2)
    first, second = snapshot.leaderboard.drivers
    updated = replace(first, pit_stops=(replace(first.pit_stops[0], exit_time=45.0),))
    assert (
        observe(
            engine, replace(snapshot, leaderboard=Leaderboard((updated, second), 2))
        )
        == ()
    )


def test_durable_restart_replay_and_completed_tombstone():
    first = EventEngine(PREFS, "synthetic")
    observe(first, sample(0))
    events = observe(first, sample(30, flag="yellow", position=1))
    data = json.loads(json.dumps(first.export()))
    second = EventEngine(PREFS, "synthetic")
    second.restore(data)
    assert observe(second, sample(0)) == ()
    assert observe(second, sample(30, flag="yellow", position=1)) == ()
    assert observe(second, sample(60, flag="yellow", position=1)) == ()
    assert observe(second, sample(90, flag="yellow", position=1)) == ()
    finish = observe(second, sample(120, flag="checkered", position=1))
    assert kinds(finish) == [EventType.FLAG]
    third = EventEngine(PREFS, "synthetic")
    third.restore(second.export())
    assert observe(third, sample(150)) == ()
    assert observe(third, sample(180, flag="checkered")) == ()
    fresh = EventEngine(PREFS, "synthetic")
    observe(fresh, sample(0))
    assert [
        event.event_id
        for event in observe(fresh, sample(30, flag="yellow", position=1))
    ] == [event.event_id for event in events]


def test_regressing_progress_even_with_newer_clock_breaks_continuity():
    engine = EventEngine(PREFS, "synthetic")
    observe(engine, sample(60, elapsed_seconds=100))
    assert observe(engine, sample(90, flag="yellow", lap=1)) == ()
    assert observe(engine, sample(120, flag="red", elapsed_seconds=50)) == ()
    assert observe(engine, sample(150, flag="red", elapsed_seconds=150)) == ()


def test_settings_are_disabled_by_default_and_changes_create_baselines():
    assert EventPreferences.from_options({}, ()).enabled is False
    engine = EventEngine(EventPreferences(), "synthetic")
    observe(engine, sample(0))
    assert observe(engine, sample(30, flag="yellow", position=1)) == ()
    changed = EventEngine(replace(PREFS, top_n=5), "synthetic")
    changed.restore(engine.export())
    assert observe(changed, sample(60, position=1)) == ()
    assert EventType.TOP_ENTER not in kinds(observe(changed, sample(90, position=1)))


def test_ledger_is_bounded_and_evicted_sessions_cannot_replay():
    engine = EventEngine(PREFS, "synthetic")
    for index in range(MAX_SESSIONS + 4):
        observe(engine, sample(index, race_id=9000 + index))
    assert len(engine.export()["sessions"]) == MAX_SESSIONS
    assert observe(engine, sample(0, race_id=9000)) == ()
    assert observe(engine, sample(1, race_id=9000, flag="yellow")) == ()
    for index in range(MAX_EVENT_IDS + 3):
        observe(
            engine,
            sample(
                1000 + index,
                race_id=9999,
                lap=100,
                flag="yellow" if index % 2 else "green",
            ),
        )
    data = engine.export()
    assert len(data["ids"]) == MAX_EVENT_IDS
    assert len(json.dumps(data)) < 170_000
    assert "leaderboard" not in json.dumps(data)
    assert "pit_stops" not in json.dumps(data)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"schema": 2},
        {"schema": 1, "sessions": {}, "ids": [None]},
        {"schema": 1, "sessions": {"bad": {}}, "ids": []},
    ],
)
def test_corrupt_storage_fails_closed(data):
    with pytest.raises(ValueError):
        EventEngine(PREFS, "synthetic").restore(data)


def test_reminder_deadlines_restart_reschedule_and_persistent_once_per_race():
    race = Race(1, 9001, "Fictional", BASE + timedelta(hours=1), season=2026)
    engine = EventEngine(PREFS, "synthetic")
    assert engine.reminders((race,), BASE) == ()
    assert engine.next_reminder(BASE) == BASE + timedelta(minutes=30)
    events = engine.reminders((race,), BASE + timedelta(minutes=30))
    assert kinds(events) == [EventType.UPCOMING]
    assert engine.reminders((race,), BASE + timedelta(minutes=31)) == ()
    restored = EventEngine(replace(PREFS, reminder_minutes=10), "synthetic")
    restored.restore(engine.export())
    assert restored.reminders((race,), BASE + timedelta(minutes=49)) == ()
    assert restored.reminders((race,), BASE + timedelta(minutes=50)) == ()
    assert restored.next_reminder(BASE) is None
    inside_window = EventEngine(PREFS, "synthetic")
    assert inside_window.reminders((race,), BASE + timedelta(minutes=31)) == ()
    rescheduled = EventEngine(PREFS, "synthetic")
    rescheduled.reminders((race,), BASE)
    assert (
        rescheduled.reminders(
            (replace(race, start_time=BASE + timedelta(minutes=40)),),
            BASE + timedelta(minutes=11),
        )
        == ()
    )


@pytest.mark.parametrize("change", ["outage", "jump", "canceled", "unknown"])
def test_reminders_do_not_backfill_or_invent_schedule_evidence(change):
    race = Race(1, 9001, "Fictional", BASE + timedelta(hours=1))
    engine = EventEngine(PREFS, "synthetic")
    engine.reminders((race,), BASE)
    if change == "outage":
        engine.reminders((), BASE + timedelta(minutes=29))
    elif change == "canceled":
        race = replace(race, status="cancelled")
    elif change == "unknown":
        race = replace(race, start_time=None)
    assert engine.reminders((race,), BASE + timedelta(minutes=32)) == ()
