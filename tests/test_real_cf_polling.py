"""Conservative discovery uses all supported sessions, without granting fast CF."""

from dataclasses import replace
from datetime import timedelta

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from test_api import Response, client_with
from test_events import BASE, sample

from custom_components.nascar_race_center import api
from custom_components.nascar_race_center.const import DOMAIN
from custom_components.nascar_race_center.coordinator import (
    LiveCoordinator,
    ScheduleCoordinator,
)
from custom_components.nascar_race_center.endpoints import LIVE_FEED
from custom_components.nascar_race_center.models import Race, Session
from custom_components.nascar_race_center.polling import legacy_decision
from custom_components.nascar_race_center.provider import CFProvider
from custom_components.nascar_race_center.timing import Leaderboard, LiveDriver


def weekend(series, practice=0, qualifying=3, race=48):
    sessions = tuple(
        Session(
            kind,
            kind,
            kind,
            BASE + timedelta(hours=start),
            BASE + timedelta(hours=start + 1),
        )
        for kind, start in [
            ("practice", practice),
            ("qualifying", qualifying),
            ("race", race),
        ]
    )
    return Race(
        series,
        9900 + series,
        "Synthetic",
        sessions[-1].start_time,
        season=BASE.year,
        sessions=sessions,
    )


@pytest.mark.parametrize("series", [1, 2, 3])
@pytest.mark.parametrize(
    "hours,reason,seconds",
    [
        (-0.25, "approaching_session", 300),
        (0.5, "scheduled_window", 300),
        (2, "between_sessions", 300),
        (2.75, "approaching_session", 300),
        (3.5, "scheduled_window", 300),
        (6, "idle", 3600),
        (47.75, "approaching_session", 300),
        (48.5, "scheduled_window", 300),
        (50, "off_season", 21600),
    ],
)
def test_practice_qualifying_race_discovery_and_end_without_asserting_activity(
    series, hours, reason, seconds
):
    result = legacy_decision(
        None, (weekend(series),), BASE + timedelta(hours=hours), 300
    )
    assert result.reason == reason
    assert result.seconds == seconds
    assert "active" not in result.reason


@pytest.mark.parametrize("kind", ["practice", "qualifying", "race"])
def test_verified_activity_still_respects_configured_conservative_minimum(kind):
    board = Leaderboard((LiveDriver(99001, is_on_track=True),), 1)
    snapshot = sample(
        0,
        status=kind,
        lap=2 if kind == "race" else None,
        flag="green" if kind == "race" else None,
        leaderboard=board,
    )
    assert legacy_decision(snapshot, (), BASE, 300).seconds == 300
    assert legacy_decision(snapshot, (), BASE, 900).seconds == 900
    assert "active" in legacy_decision(snapshot, (), BASE, 300).reason


def test_missing_ambiguous_canceled_and_distant_schedules_are_bounded():
    assert legacy_decision(None, (), BASE, 300, schedules_known=False).seconds == 3600
    assert (
        legacy_decision(None, (Race(1, 9901, "Unknown"),), BASE, 300).reason
        == "conservative_fallback"
    )
    assert legacy_decision(None, (), BASE, 300).seconds == 21600
    assert (
        legacy_decision(
            None,
            (weekend(1, practice=30 * 24, qualifying=31 * 24, race=32 * 24),),
            BASE,
            300,
        ).seconds
        == 21600
    )
    canceled = replace(weekend(1), status="canceled")
    assert legacy_decision(None, (canceled,), BASE, 300).seconds == 21600
    approaching = weekend(2, practice=2 / 3)
    # Wake at the approach boundary in ten minutes; never six hours later.
    assert legacy_decision(None, (approaching,), BASE, 300).seconds == 600
    assert (
        legacy_decision(None, (approaching,), BASE + timedelta(minutes=10), 300).seconds
        == 300
    )


async def test_one_global_cf_coordinator_discovers_peer_session_despite_retained_source(
    hass, freezer, monkeypatch
):
    freezer.move_to(BASE)
    monkeypatch.setattr(api, "_monotonic", lambda: 1000)
    client, session = client_with(Response(body=b"null"))
    provider = CFProvider(session)
    provider.api = client
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    schedule = ScheduleCoordinator(hass, entry, provider, (1, 2, 3))
    schedule.data = replace(
        schedule.data,
        races={1: (), 2: (weekend(2, practice=0.25),), 3: ()},
        failed_series=frozenset(),
        updated_at={1: BASE, 2: BASE, 3: BASE},
    )
    live = LiveCoordinator(hass, entry, provider, schedule, 300)
    live._stale_reads = 5
    live._observed_context = (1, 9901, 7)
    live.observation_state = "clock_unchanged"
    retained = sample(-3600, flag="cold_track")
    live.data = retained
    try:
        assert live._next_interval(retained) == timedelta(seconds=900)
        assert live.poll_decision.reason == "approaching_session"
        assert live.polling_diagnostics()["fast_permitted"] is False
        assert not live.view(1).available
        assert live.view(2).snapshot is None
        assert session.get.call_count == 0
        # Existing endpoint cooldown still dominates a valid session opportunity.
        client._cooldowns[LIVE_FEED] = (8200, 403)
        assert live._next_interval(retained) == timedelta(seconds=7200)
        assert live.interval_constraint == "cache_or_cooldown"
        assert session.get.call_count == 0
    finally:
        await live.async_shutdown()
        await schedule.async_shutdown()
