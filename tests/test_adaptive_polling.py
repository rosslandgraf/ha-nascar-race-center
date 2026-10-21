"""Handmade normalized observations: no NASCAR traffic or invented CF fields."""

import asyncio
import json
from dataclasses import replace
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from test_api import Response, client_with
from test_events import BASE, sample
from test_phase3a_sensors import state

from custom_components.nascar_race_center import api
from custom_components.nascar_race_center.const import DOMAIN
from custom_components.nascar_race_center.coordinator import (
    LiveCoordinator,
    ScheduleCoordinator,
)
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nascar_race_center.endpoints import LIVE_FEED
from custom_components.nascar_race_center.events import EVENT_NAMESPACE, EventType
from custom_components.nascar_race_center.models import (
    PollingDeferred,
    ProviderError,
    Race,
    Session,
    parse_live,
)
from custom_components.nascar_race_center.polling import (
    CF_LIMITS,
    active_kind,
    adaptive_decision,
)
from custom_components.nascar_race_center.polling_storage import LiveRequestGuard
from custom_components.nascar_race_center.provider import CFProvider, DemoProvider
from custom_components.nascar_race_center.timing import Leaderboard, LiveDriver


def decision(races=(), snapshot=None, known=True, now=BASE):
    return adaptive_decision(
        snapshot, races, now, schedules_known=known, approaching_seconds=30
    )


def weekend(*, first=0, next_start=3, race_start=24):
    return Race(
        1,
        9001,
        "Synthetic weekend",
        BASE + timedelta(hours=race_start),
        sessions=(
            Session(
                "p",
                "Practice",
                "practice",
                BASE + timedelta(hours=first),
                BASE + timedelta(hours=first + 1),
            ),
            Session(
                "q",
                "Qualifying",
                "qualifying",
                BASE + timedelta(hours=next_start),
                BASE + timedelta(hours=next_start + 1),
            ),
        ),
    )


@pytest.mark.parametrize("kind", ["race", "practice", "qualifying"])
@pytest.mark.parametrize("lap", [None, 0, 1])
def test_supported_activity_without_race_only_practice_requirements(kind, lap):
    board = Leaderboard((LiveDriver(99001, is_on_track=True, laps_completed=lap),), 1)
    snapshot = sample(
        0,
        status=kind,
        lap=lap,
        flag="green" if kind == "race" else None,
        leaderboard=board,
    )
    expected = kind if kind != "race" or lap == 1 else None
    assert active_kind(snapshot, BASE) == expected
    assert decision(snapshot=snapshot).seconds == (10 if expected else 21600)


@pytest.mark.parametrize(
    "changes",
    [
        {"run_id": None},
        {"run_id": 0},
        {"race_id": 0},
        {"status": None},
        {"source_updated_at": None},
        {"source_updated_at": BASE + timedelta(seconds=1)},
        {"source_updated_at": BASE - timedelta(hours=1)},
        {"flag": "checkered"},
        {"flag": "cold_track"},
    ],
)
def test_incomplete_or_stale_source_cannot_assert_activity(changes):
    assert active_kind(sample(0, **changes), BASE) is None


@pytest.mark.parametrize("on_track", [False, None])
def test_session_kind_alone_cannot_establish_practice(on_track):
    snapshot = sample(
        0,
        status="practice",
        lap=0,
        flag=None,
        leaderboard=Leaderboard((LiveDriver(99001, is_on_track=on_track),), 1),
    )
    assert active_kind(snapshot, BASE) is None


@pytest.mark.parametrize(
    ("race", "seconds", "reason"),
    [
        (Race(1, 1, "Soon", BASE + timedelta(minutes=15)), 30, "approaching_session"),
        (weekend(first=-2), 300, "between_sessions"),
        (weekend(first=-2, next_start=15), 3600, "idle"),
        (weekend(first=-48, next_start=-24, race_start=-10), 21600, "off_season"),
        (Race(1, 1, "Tomorrow", BASE + timedelta(days=1)), 3600, "idle"),
        (Race(1, 1, "Unknown"), 3600, "conservative_fallback"),
        (Race(1, 1, "Next month", BASE + timedelta(days=30)), 21600, "off_season"),
        (Race(1, 1, "Just scheduled", BASE), 300, "scheduled_window"),
        (
            Race(1, 1, "Missed unknown duration", BASE - timedelta(hours=1)),
            3600,
            "conservative_fallback",
        ),
    ],
)
def test_schedule_discovery_idle_overnight_and_weekend_end(race, seconds, reason):
    result = decision((race,))
    assert (result.seconds, result.reason) == (seconds, reason)
    assert not result.reason.startswith("active")


def test_missing_schedules_cancellation_offsets_and_approach_boundary():
    assert decision(known=False).reason == "conservative_fallback"
    assert decision().seconds == 21600
    canceled = Race(1, 1, "Canceled", BASE + timedelta(minutes=5), status="canceled")
    assert decision((canceled,)).seconds == 21600
    approaching = Race(2, 2, "Series 2", BASE + timedelta(minutes=40))
    assert decision((weekend(first=-2, next_start=15), approaching)).seconds == 600
    assert decision((approaching,), now=BASE + timedelta(minutes=10)).seconds == 30
    # A datetime's explicit offset is normalized by the existing parser, never
    # derived from track, server Date or a *_utc field name.
    from custom_components.nascar_race_center.models import parse_schedule

    race = parse_schedule(
        {
            "series_1": [
                {
                    "race_id": 1,
                    "series_id": 1,
                    "race_name": "Unknown zone",
                    "date_scheduled": "2026-10-21T16:05:00",
                }
            ]
        },
        1,
    )[0]
    assert decision((race,)).reason == "conservative_fallback"


class SyntheticProvider(DemoProvider):
    """An offline source advancing at the test clock, with one global read."""

    def __init__(self):
        self.reads = []
        self.kind = "race"
        self.fail = None
        self.frozen = False
        self.races = ()
        self.position = 12

    async def async_get_schedule(self, year, series_id):
        return tuple(race for race in self.races if race.series_id == series_id)

    async def async_get_live(self):
        now = dt_util.utcnow()
        self.reads.append(now)
        if self.fail:
            raise self.fail
        second = 0 if self.frozen else int((now - BASE).total_seconds())
        snapshot = sample(
            second,
            position=self.position,
            flag="yellow" if second >= 30 else "green",
            lap=10,
        )
        if self.kind != "race":
            snapshot = replace(
                snapshot,
                status=self.kind,
                flag=None,
                lap=None,
                leaderboard=Leaderboard(
                    (LiveDriver(99001, position=12, is_on_track=True),), 1
                ),
            )
        return snapshot


async def setup_synthetic(
    hass, provider, *, favorites=("99001",), series=("1", "2", "3"), events=True
):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "provider": "demo",
            "series": list(series),
            "favorite_drivers": list(favorites),
            "live_polling_policy": "adaptive",
            "approaching_interval": 30,
            "racing_events": events,
            "event_types": [EventType.FLAG.value],
        },
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


@pytest.mark.parametrize("kind", ["race", "practice", "qualifying"])
@pytest.mark.parametrize(
    "favorites", [("99001",), tuple(str(x) for x in range(99001, 99011))]
)
async def test_measured_scheduled_ten_second_path_entities_events_and_unload(
    hass, freezer, kind, favorites
):
    freezer.move_to(BASE)
    provider = SyntheticProvider()
    provider.kind = kind
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    entry = await setup_synthetic(hass, provider, favorites=favorites)
    runtime = entry.runtime_data
    assert runtime.live.update_interval == timedelta(seconds=10)
    initial_state = state(hass, entry, "driver_99001_live_position")
    assert initial_state.state == "12"
    for index in range(1, 61):
        freezer.move_to(BASE + timedelta(seconds=index * 10))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
        assert runtime.live.update_interval == timedelta(seconds=10)
        # Consumers of the normalized field have no provider I/O side effects.
        for series in (1, 2, 3):
            runtime.live.view(series).driver(99001)
        await async_get_config_entry_diagnostics(hass, entry)
    assert len(provider.reads) == 61  # one startup + 60 eligible scheduled reads
    assert {
        (b - a).total_seconds()
        for a, b in zip(provider.reads, provider.reads[1:], strict=False)
    } == {10}
    assert (
        state(hass, entry, "driver_99001_live_position").last_changed
        == initial_state.last_changed
    )
    assert len(seen) == (1 if kind == "race" else 0)
    if seen:
        assert seen[0]["event_type"] == EventType.FLAG
        assert seen[0]["source_time"] == (BASE + timedelta(seconds=30)).isoformat()
        ledger = await runtime.events.store.async_load()
        assert seen[0]["event_id"] in ledger["ids"]
    assert await hass.config_entries.async_unload(entry.entry_id)
    freezer.move_to(BASE + timedelta(hours=7))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(provider.reads) == 61
    assert runtime.live._unsub_source_expiry is None


async def test_frozen_and_regressing_clocks_back_off_then_recover(hass, freezer):
    freezer.move_to(BASE)
    provider = SyntheticProvider()
    entry = await setup_synthetic(hass, provider)
    provider.frozen = True
    for second in (10, 20, 30, 40, 50, 60):
        freezer.move_to(BASE + timedelta(seconds=second))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
    assert entry.runtime_data.live.update_interval >= timedelta(seconds=300)
    freezer.move_to(BASE + timedelta(seconds=360))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entry.runtime_data.live.update_interval >= timedelta(seconds=600)
    provider.frozen = False
    freezer.move_to(BASE + timedelta(seconds=960))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert entry.runtime_data.live.update_interval == timedelta(seconds=10)
    provider.async_get_live = AsyncMock(
        return_value=sample(900, series_id=2, run_id=19)
    )
    await entry.runtime_data.live.async_refresh()
    assert (
        entry.runtime_data.live.polling_diagnostics()["constraint"]
        == "source_not_advancing"
    )
    assert entry.runtime_data.live.update_interval >= timedelta(seconds=300)
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize("status", [403, 429, 503])
async def test_scheduled_failures_retry_hint_backoff_and_recovery(
    hass, freezer, status
):
    freezer.move_to(BASE)
    provider = SyntheticProvider()
    entry = await setup_synthetic(hass, provider)
    provider.fail = ProviderError("Synthetic failure", status=status, retry_after=600)
    freezer.tick(10)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(provider.reads) == 2
    assert entry.runtime_data.live.update_interval >= timedelta(seconds=600)
    for _ in range(59):
        freezer.tick(10)
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
    assert len(provider.reads) == 2
    provider.fail = None
    freezer.tick(10)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(provider.reads) == 3
    assert entry.runtime_data.live.update_interval == timedelta(seconds=10)
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_schedule_revision_rearms_one_existing_poll_without_immediate_io(
    hass, freezer
):
    freezer.move_to(BASE)
    provider = SyntheticProvider()
    provider.async_get_live = AsyncMock(return_value=None)
    entry = await setup_synthetic(hass, provider, events=False)
    assert entry.runtime_data.live.update_interval == timedelta(hours=6)
    provider.races = (Race(2, 99, "Revised session", BASE + timedelta(minutes=15)),)
    await entry.runtime_data.schedule.async_refresh()
    await hass.async_block_till_done()
    assert provider.async_get_live.await_count == 1
    assert entry.runtime_data.live.update_interval == timedelta(seconds=30)
    freezer.tick(30)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert provider.async_get_live.await_count == 2
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_short_cache_fallback_upstream_lifetimes_and_304(
    monkeypatch,
):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    body = json.dumps(
        {
            "series_id": 1,
            "race_id": 9001,
            "run_id": 8,
            "run_type": 3,
            "flag_state": 1,
            "lap_number": 10,
            "time_of_day_os": BASE.isoformat(),
        }
    ).encode()
    client, session = client_with(
        Response(body=body, headers={"ETag": '"one"'}),
        Response(304, headers={"Cache-Control": "max-age=120"}),
        Response(body=body, headers={"Cache-Control": "max-age=172800"}),
        Response(body=body),
    )
    for second in (0, 9, 10, 119, 129, 130, 86530, 172929, 172930):
        clock[0] = 1000 + second
        result = parse_live(
            await client.async_get_json(LIVE_FEED, minimum_ttl=10, minimum_interval=10)
        )
        assert result.source_updated_at == BASE
        if second < 10:
            assert session.get.call_count == 1
        elif second < 130:
            assert session.get.call_count == 2
        elif second < 172930:
            assert session.get.call_count == 3
    assert session.get.call_count == 4
    assert session.get.call_args_list[1].kwargs["headers"]["If-None-Match"] == '"one"'


@pytest.mark.parametrize(
    "headers", [{"Cache-Control": "no-cache"}, {"Cache-Control": "no-store"}]
)
async def test_one_request_per_eligible_slot_under_concurrency(headers, monkeypatch):
    monkeypatch.setattr(api, "_monotonic", lambda: 1000)
    client, session = client_with(Response(headers=headers))
    results = await asyncio.gather(
        *(
            client.async_get_json(LIVE_FEED, minimum_ttl=10, minimum_interval=10)
            for _ in range(20)
        ),
        return_exceptions=True,
    )
    assert session.get.call_count == 1
    assert sum(isinstance(x, PollingDeferred) for x in results) == 19


@pytest.mark.parametrize("status", [200, 304, 403, 429, 503])
async def test_retry_after_is_honored_on_every_response(status, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(
        Response(headers={"Cache-Control": "no-cache"}),
        Response(status, headers={"Retry-After": "600", "Cache-Control": "no-cache"}),
    )
    await client.async_get_json(LIVE_FEED)
    if status in (200, 304):
        await client.async_get_json(LIVE_FEED)
    else:
        with pytest.raises(ProviderError):
            await client.async_get_json(LIVE_FEED)
    assert client.request_delay(LIVE_FEED) >= 600
    with pytest.raises(ProviderError):
        await client.async_get_json(LIVE_FEED)
    assert session.get.call_count == 2


async def test_cf_defaults_and_adaptive_option_cannot_grant_fast_permission(
    hass, freezer, monkeypatch
):
    freezer.move_to(BASE)
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(Response(body=b"null"), Response(body=b"null"))
    provider = CFProvider(session)
    provider.api = client
    for second in range(300):
        clock[0] = 1000 + second
        await provider.async_get_live()
    assert session.get.call_count == 1
    clock[0] = 1300
    await provider.async_get_live()
    assert session.get.call_count == 2
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    schedule = ScheduleCoordinator(hass, entry, provider, (1,))
    schedule.data = replace(
        schedule.data,
        races={1: (Race(1, 1, "Soon", BASE + timedelta(minutes=5)),)},
        failed_series=frozenset(),
        updated_at={1: BASE},
    )
    live = LiveCoordinator(
        hass, entry, provider, schedule, 300, polling_policy="adaptive"
    )
    assert live._next_interval(sample(0)) == timedelta(seconds=300)
    assert live.polling_diagnostics()["fast_permitted"] is False
    assert live._next_interval(None) == timedelta(seconds=900)
    assert live.polling_diagnostics()["constraint"] == "provider_policy"
    assert provider.polling_limits == CF_LIMITS
    await live.async_shutdown()
    await schedule.async_shutdown()


async def test_persisted_reservation_restart_server_cooldown_and_no_payload(
    hass, freezer, monkeypatch
):
    freezer.move_to(BASE)
    monkeypatch.setattr(api, "_monotonic", lambda: 1000)
    guard = LiveRequestGuard(hass, "synthetic-entry")
    await guard.async_load()
    client, session = client_with(Response(429, headers={"Retry-After": "900"}))
    client.live_guard = guard
    with pytest.raises(ProviderError):
        await client.async_get_json(LIVE_FEED, minimum_interval=300)
    data = await guard.store.async_load()
    assert data == {
        "not_before": (BASE + timedelta(seconds=900)).isoformat(),
        "host_not_before": (BASE + timedelta(seconds=900)).isoformat(),
    }
    restored = LiveRequestGuard(hass, "synthetic-entry")
    await restored.async_load()
    fresh, new_session = client_with(Response())
    fresh.live_guard = restored
    with pytest.raises(ProviderError):
        await fresh.async_get_json(LIVE_FEED, minimum_interval=300)
    with pytest.raises(ProviderError):
        await fresh.async_get_json("/cacher/2026/race_list_basic.json")
    new_session.get.assert_not_called()
    freezer.tick(900)
    await fresh.async_get_json(LIVE_FEED, minimum_interval=300)
    assert new_session.get.call_count == 1


async def test_cancelled_attempt_keeps_restart_reservation(hass, freezer):
    freezer.move_to(BASE)
    guard = LiveRequestGuard(hass, "cancelled-entry")
    await guard.async_load()
    client, _ = client_with(asyncio.CancelledError())
    client.live_guard = guard
    with pytest.raises(asyncio.CancelledError):
        await client.async_get_json(LIVE_FEED, minimum_interval=300)
    restored = LiveRequestGuard(hass, "cancelled-entry")
    await restored.async_load()
    assert restored.remaining == 300


async def test_guard_write_failure_blocks_live_io(hass, freezer):
    freezer.move_to(BASE)
    guard = LiveRequestGuard(hass, "failed-entry")
    await guard.async_load()
    client, session = client_with(Response())
    client.live_guard = guard
    with patch.object(guard.store, "async_save", AsyncMock()):
        with pytest.raises(ProviderError):
            await client.async_get_json(LIVE_FEED, minimum_interval=300)
    session.get.assert_not_called()
    assert guard.failed


async def test_invalid_persisted_host_clock_fails_closed_without_breaking_schedule(
    hass, freezer
):
    freezer.move_to(BASE)
    guard = LiveRequestGuard(hass, "malformed-entry")
    await guard.store.async_save(
        {"not_before": BASE.isoformat(), "host_not_before": "2026-10-21T16:00:00"}
    )
    await guard.async_load()
    assert guard.failed
    client, session = client_with(Response())
    client.live_guard = guard
    with pytest.raises(ProviderError):
        await client.async_get_json(LIVE_FEED, minimum_interval=300)
    assert await client.async_get_json("/cacher/2026/race_list_basic.json") == {
        "series_1": []
    }
    assert session.get.call_count == 1


async def test_expires_and_date_do_not_double_subtract_response_age(
    freezer, monkeypatch
):
    from email.utils import format_datetime

    freezer.move_to(BASE)
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(
        Response(
            headers={
                "Date": format_datetime(BASE - timedelta(seconds=60)),
                "Expires": format_datetime(BASE + timedelta(seconds=60)),
            }
        ),
        Response(),
    )
    await client.async_get_json(LIVE_FEED, minimum_ttl=10)
    clock[0] += 59
    await client.async_get_json(LIVE_FEED, minimum_ttl=10)
    assert session.get.call_count == 1
    clock[0] += 1
    await client.async_get_json(LIVE_FEED, minimum_ttl=10)
    assert session.get.call_count == 2


async def test_304_without_age_does_not_reuse_previous_response_age(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(
        Response(headers={"Cache-Control": "max-age=120", "Age": "110"}),
        Response(304),
        Response(),
    )
    await client.async_get_json(LIVE_FEED)
    clock[0] += 10
    await client.async_get_json(LIVE_FEED)
    clock[0] += 119
    await client.async_get_json(LIVE_FEED)
    assert session.get.call_count == 2
    clock[0] += 1
    await client.async_get_json(LIVE_FEED)
    assert session.get.call_count == 3


async def test_expired_upstream_freshness_defers_before_local_request_floor(
    monkeypatch,
):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(
        Response(
            headers={"Cache-Control": "max-age=5, must-revalidate", "ETag": '"one"'}
        ),
        Response(304),
    )
    await client.async_get_json(LIVE_FEED, minimum_interval=10)
    clock[0] += 6
    with pytest.raises(PollingDeferred):
        await client.async_get_json(LIVE_FEED, minimum_interval=10)
    assert client.diagnostics()[LIVE_FEED]["delivery"] == "cooldown"
    assert session.get.call_count == 1
    clock[0] += 4
    await client.async_get_json(LIVE_FEED, minimum_interval=10)
    assert session.get.call_count == 2
    assert session.get.call_args.kwargs["headers"]["If-None-Match"] == '"one"'
