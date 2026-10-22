"""Session schedule contracts, identity and independent enrichment failures."""

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.nascar_race_center.endpoints import (
    schedule_feed_path,
    schedule_path,
)
from custom_components.nascar_race_center.models import (
    ProviderError,
    Race,
    SchemaError,
    merge_schedule,
    parse_schedule,
    parse_schedule_feed,
)
from custom_components.nascar_race_center.provider import CFProvider, DemoProvider


def _rows() -> list[dict[str, object]]:
    return json.loads(
        (
            Path(__file__).parent / "fixtures" / "nascar" / "session_schedule.json"
        ).read_text()
    )


@pytest.mark.parametrize("failure", [ProviderError("Unavailable", status=503), {}])
async def test_empty_optional_details_cannot_mask_basic_schedule_failure(
    failure: object,
) -> None:
    """No enrichment is not evidence of an empty authoritative season list."""
    provider = CFProvider(MagicMock())
    provider.api.async_get_json = AsyncMock(side_effect=[failure, []])
    with pytest.raises(ProviderError):
        await provider.async_get_schedule(2026, 1)


@pytest.mark.parametrize("series_id", [1, 2, 3])
def test_series_sessions_span_year_boundary(series_id: int) -> None:
    """Sessions retain the requested season even when dates cross the year."""
    rows = _rows()
    for row in rows:
        row["series_id"] = series_id
    race = parse_schedule_feed(rows, series_id, 2026)[0]
    assert race.series_id == series_id
    assert race.season == 2026
    assert race.track_id == 99001
    assert race.start_time == datetime(2027, 1, 2, 18, tzinfo=UTC)
    assert [session.kind for session in race.sessions] == [
        "practice",
        "qualifying",
        "race",
    ]
    assert race.sessions[0].start_time == datetime(2026, 12, 31, 18, tzinfo=UTC)
    assert race.sessions[-1].end_time == datetime(2027, 1, 2, 21, tzinfo=UTC)
    assert all(session.status is None for session in race.sessions)


def test_session_identity_survives_postponement_and_reordering() -> None:
    """A new time and changed source order replace the same named session."""
    rows = _rows()
    original = parse_schedule_feed(rows, 1, 2026)[0]
    rows[0]["start_time_utc"] = "2027-01-01T18:00:00Z"
    rows[0]["end_time_utc"] = "2027-01-01T19:00:00Z"
    postponed = parse_schedule_feed(list(reversed(rows)), 1, 2026)[0]
    before = {session.name: session for session in original.sessions}
    after = {session.name: session for session in postponed.sessions}
    assert before["Practice 1"].session_id == after["Practice 1"].session_id
    assert before["Practice 1"].start_time != after["Practice 1"].start_time
    assert {session.session_id for session in original.sessions} == {
        session.session_id for session in postponed.sessions
    }
    assert (
        before["Race"].session_id
        != parse_schedule_feed(rows, 1, 2027)[0].sessions[-1].session_id
    )


@pytest.mark.parametrize(
    "timestamp", [None, "", "2026-12-31", "0001-01-01T00:00:00", "bad"]
)
def test_uncertain_session_timestamps_are_unknown(timestamp: object) -> None:
    """Missing, date-only and sentinel inputs remain unknown; no local fallback."""
    rows = _rows()[:1]
    rows[0]["start_time_utc"] = timestamp
    rows[0]["start_time"] = "2026-12-31T13:00:00-05:00"
    session = parse_schedule_feed(rows, 1, 2026)[0].sessions[0]
    assert session.start_time is None
    assert session.end_time is None


@pytest.mark.parametrize(
    "end", [None, "bad", "2026-12-31T17:00:00Z", "2026-12-31T18:00:00Z"]
)
def test_invalid_or_missing_duration_is_not_estimated(end: object) -> None:
    """Known start survives an invalid end without estimating a duration."""
    rows = _rows()[:1]
    rows[0]["end_time_utc"] = end
    session = parse_schedule_feed(rows, 1, 2026)[0].sessions[0]
    assert session.start_time is not None
    assert session.end_time is None


def test_source_offsets_handle_both_dst_transitions() -> None:
    """Explicit offsets preserve elapsed time over spring and fall changes."""
    rows = _rows()[:1]
    rows[0].update(
        start_time_utc="2026-03-08T01:30:00-05:00",
        end_time_utc="2026-03-08T03:30:00-04:00",
    )
    spring = parse_schedule_feed(rows, 1, 2026)[0].sessions[0]
    assert spring.end_time - spring.start_time == timedelta(hours=1)
    rows[0].update(
        start_time_utc="2026-11-01T01:30:00-04:00",
        end_time_utc="2026-11-01T01:30:00-05:00",
    )
    fall = parse_schedule_feed(rows, 1, 2026)[0].sessions[0]
    assert fall.end_time - fall.start_time == timedelta(hours=1)


@pytest.mark.parametrize("payload", [None, {}, {"schedule": []}, [None]])
def test_unknown_detail_shapes_fail_explicitly(payload: object) -> None:
    with pytest.raises(SchemaError):
        parse_schedule_feed(payload, 1, 2026)


def test_bad_or_ambiguous_session_identity_is_not_invented() -> None:
    rows = _rows()
    with pytest.raises(SchemaError, match="duplicate"):
        parse_schedule_feed([rows[0], dict(rows[0])], 1, 2026)
    rows[0]["series_id"] = 2
    with pytest.raises(SchemaError, match="identity"):
        parse_schedule_feed(rows, 1, 2026)
    rows[0]["series_id"] = 1
    rows[0]["event_name"] = ""
    with pytest.raises(SchemaError, match="name"):
        parse_schedule_feed(rows, 1, 2026)


def test_nested_basic_sessions_use_only_documented_fields() -> None:
    """Unknown ends/status are ignored; source notes remain plain text."""
    race = parse_schedule(
        {
            "series_1": [
                {
                    "race_id": 9901,
                    "series_id": 1,
                    "race_name": "Fictional Weekend",
                    "race_season": 2026,
                    "track_id": 99001,
                    "schedule": [
                        {
                            "event_name": "Practice",
                            "run_type": 1,
                            "start_time_utc": "2026-12-31T18:00:00Z",
                            "notes": "Schedule subject to change",
                            "end_time_utc": "2026-12-31T19:00:00Z",
                            "status": "canceled",
                        }
                    ],
                }
            ]
        },
        1,
        year=2026,
    )[0]
    assert race.season == 2026
    assert race.track_id == 99001
    assert race.sessions[0].notes == "Schedule subject to change"
    assert race.sessions[0].end_time is None
    assert race.sessions[0].status is None


def test_detailed_schedule_replaces_removed_sessions_and_updates_race() -> None:
    detailed = parse_schedule_feed(_rows(), 1, 2026)
    basic = (
        replace(detailed[0], start_time=datetime(2027, 1, 1, 18, tzinfo=UTC)),
        Race(1, 9999, "Basic-only race", season=2026),
    )
    removed = parse_schedule_feed(_rows()[1:], 1, 2026)
    merged = merge_schedule(basic, removed)
    assert len(merged) == 2
    assert [session.kind for session in merged[0].sessions] == ["qualifying", "race"]
    assert merged[0].start_time == datetime(2027, 1, 2, 18, tzinfo=UTC)
    assert merged[1].race_id == 9999
    assert merge_schedule(basic, ()) == basic


def test_multiple_race_sessions_do_not_choose_arbitrary_race_time() -> None:
    rows = _rows()[-1:]
    other = dict(rows[0], event_name="Second Heat")
    assert parse_schedule_feed([*rows, other], 1, 2026)[0].start_time is None


@pytest.mark.parametrize("detail_case", ["unknown", "multiple", "practice_only"])
def test_detailed_unknown_race_start_does_not_resurrect_old_basic_time(
    detail_case: str,
) -> None:
    """A published TBD race supersedes its old time under the same identity."""
    basic = (
        Race(
            1,
            9901,
            "Old Race Title",
            datetime(2027, 1, 2, 18, tzinfo=UTC),
            season=2026,
        ),
    )
    rows = _rows()[-1:]
    if detail_case == "unknown":
        rows[0]["start_time_utc"] = "2027-01-03"
    elif detail_case == "multiple":
        rows.append(dict(rows[0], event_name="Second Heat"))
    else:
        rows = _rows()[:1]
    detailed = parse_schedule_feed(rows, 1, 2026)
    merged = merge_schedule(basic, detailed)[0]
    assert merged.race_id == basic[0].race_id
    assert merged.name == "Fictional Year Boundary Weekend"
    assert merged.start_time == (
        basic[0].start_time if detail_case == "practice_only" else None
    )


def test_optional_session_metadata_cannot_erase_known_venue() -> None:
    """A sparse session row can reuse metadata from another row in its race."""
    rows = _rows()
    for row in rows[1:]:
        row.pop("track_id")
        row.pop("track_name")
    race = parse_schedule_feed(rows, 1, 2026)[0]
    assert race.track_id == 99001
    assert race.track == "Demonstration Speedway"


def test_unreasonably_large_provider_integers_fail_safely() -> None:
    """Python's integer conversion limit is an upstream schema failure."""
    rows = _rows()[:1]
    rows[0]["run_type"] = "9" * 5000
    assert parse_schedule_feed(rows, 1, 2026)[0].sessions[0].kind is None
    rows[0]["race_id"] = "9" * 5000
    with pytest.raises(SchemaError, match="identity"):
        parse_schedule_feed(rows, 1, 2026)


@pytest.mark.parametrize("schedule", [{}, [None], [{"event_name": ""}]])
def test_malformed_optional_nested_sessions_preserve_core_race(schedule) -> None:
    race = parse_schedule(
        {
            "series_1": [
                {
                    "race_id": 9901,
                    "series_id": 1,
                    "race_name": "Fictional Weekend",
                    "date_scheduled": "2027-01-02T18:00:00Z",
                    "schedule": schedule,
                }
            ]
        },
        1,
        year=2026,
    )[0]
    assert race.race_id == 9901
    assert race.start_time == datetime(2027, 1, 2, 18, tzinfo=UTC)
    assert race.sessions_failed
    assert race.sessions == ()
    assert not merge_schedule((race,), parse_schedule_feed(_rows(), 1, 2026))[
        0
    ].sessions_failed


async def test_optional_detail_failure_preserves_basic_and_recovers() -> None:
    provider = CFProvider(MagicMock())
    basic = {
        "series_1": [
            {
                "race_id": 9901,
                "series_id": 1,
                "race_name": "Fictional Weekend",
                "date_scheduled": "2027-01-01T18:00:00Z",
            }
        ]
    }
    provider.api.async_get_json = AsyncMock(
        side_effect=[basic, ProviderError("Unpublished", status=404), basic, _rows()]
    )
    races = await provider.async_get_schedule(2026, 1)
    assert races[0].start_time == datetime(2027, 1, 1, 18, tzinfo=UTC)
    assert (2026, 1) in provider.schedule_details_failed
    enriched = await provider.async_get_schedule(2026, 1)
    assert len(enriched[0].sessions) == 3
    assert enriched[0].start_time == datetime(2027, 1, 2, 18, tzinfo=UTC)
    assert not provider.schedule_details_failed
    assert provider.api.async_get_json.call_args_list[0].args == (schedule_path(2026),)
    assert provider.api.async_get_json.call_args_list[1].args == (
        schedule_feed_path(2026, 1),
    )


async def test_schedule_detail_can_survive_basic_feed_outage() -> None:
    provider = CFProvider(MagicMock())
    provider.api.async_get_json = AsyncMock(
        side_effect=[ProviderError("Outage"), _rows()]
    )
    assert len((await provider.async_get_schedule(2026, 1))[0].sessions) == 3
    provider.api.async_get_json = AsyncMock(side_effect=ProviderError("Outage"))
    with pytest.raises(ProviderError):
        await provider.async_get_schedule(2026, 1)


async def test_demo_preserves_race_identity_with_weekend_metadata() -> None:
    for series_id in (1, 2, 3):
        races = await DemoProvider().async_get_schedule(2026, series_id)
        assert len(races) == 2
        assert races[0].race_id == 202600 + series_id
        assert races[0].start_time == datetime(2026, 2, 15, 19, tzinfo=UTC)
        assert len(races[0].sessions) == 3
        assert races[0].sessions[0].start_time.day == 13
