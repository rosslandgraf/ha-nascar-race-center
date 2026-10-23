"""Small cached bootstrap, schedule and live projections. Never perform I/O."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from homeassistant.util import dt as dt_util

from .const import CONF_PROVIDER, PROVIDER_DEMO, REFERENCE_STALE_AFTER
from .dashboard_schema import fields, project
from .models import Race, Session

if TYPE_CHECKING:
    from . import NascarConfigEntry

LIMITATIONS = (
    "experimental_source_semantics",
    "no_official_finality_or_championship_inference",
    "global_live_feed_reports_one_series",
    "source_timing_units_unverified",
    "only_named_utc_schedule_fields_accept_naive_times",
    "standalone_scoring_requires_verified_association",
    "historical_path_context_does_not_certify_content_identity",
)


def race_summary(race: Race) -> dict[str, Any]:
    result = fields(
        race,
        (
            "series_id season race_id name start_time track track_id status"
            " sessions_failed"
        ),
    )
    result["session_count"] = len(race.sessions)
    result["time_availability"] = (
        "available" if race.start_time else "unknown_source_timezone_or_time"
    )
    return result


def bootstrap(entry: NascarConfigEntry) -> dict[str, Any]:
    runtime = entry.runtime_data
    now = dt_util.utcnow()
    reference = runtime.reference.data

    def reference_health(kind: str) -> str:
        updated = reference.updated_at.get(kind)
        if kind in reference.failed_feeds or updated is None:
            return "unavailable"
        return "stale" if now - updated > REFERENCE_STALE_AFTER else "available"

    def future_times(race: Race) -> list[datetime]:
        values = [
            session.start_time
            for session in race.sessions
            if session.start_time is not None
            and session.kind in {"practice", "qualifying", "race"}
            and session.start_time >= now
            and session.status not in ("canceled", "cancelled", "completed")
        ]
        if race.start_time is not None and race.start_time >= now:
            values.append(race.start_time)
        return values

    upcoming = [
        race
        for series in runtime.schedule.series
        for race in runtime.schedule.usable_races(series)
        if race.status not in ("canceled", "cancelled", "completed")
        and future_times(race)
    ]
    upcoming.sort(key=lambda race: min(future_times(race)))
    compact = [
        race
        for series in runtime.schedule.series
        for race in [r for r in upcoming if r.series_id == series][:2]
    ]
    activity: list[tuple[datetime, Race, Session | None]] = [
        (s.start_time, r, s)
        for r in upcoming
        for s in r.sessions
        if s.start_time is not None
        and s.kind in {"practice", "qualifying", "race"}
        and s.start_time >= now
        and s.status not in ("canceled", "cancelled", "completed")
    ]
    # A known race start remains useful when weekend session enrichment is absent.
    activity.extend(
        (r.start_time, r, None)
        for r in upcoming
        if r.start_time is not None and r.start_time >= now
    )
    next_activity = min(activity, key=lambda item: item[0]) if activity else None
    tracks = {r.track_id for r in compact}

    def compact_sessions(race: Race) -> tuple[Session, ...]:
        # Put the next supported activities into the bounded bootstrap rather
        # than letting old/unsorted garage rows hide the next real session.
        return tuple(
            sorted(
                race.sessions,
                key=lambda session: (
                    0
                    if session.kind in {"practice", "qualifying", "race"}
                    and session.start_time is not None
                    and session.start_time >= now
                    and session.status not in {"canceled", "cancelled", "completed"}
                    else 1,
                    session.start_time or datetime.max.replace(tzinfo=dt_util.UTC),
                    session.session_id,
                ),
            )[:4]
        )

    return {
        "series_ids": list(runtime.schedule.series),
        "favorite_driver_ids": [str(i) for i in runtime.favorites.ids],
        "references": {
            "drivers_status": reference_health("drivers"),
            "tracks_status": reference_health("tracks"),
            "unresolved_favorites": [
                {"driver_id": str(i), "reason": "reference_unavailable_or_missing"}
                for i in runtime.favorites.ids
                if reference_health("drivers") != "available"
                or i not in reference.drivers
            ],
            "drivers": [
                {
                    "driver_id": str(d.driver_id),
                    "name": d.name,
                    "associations": [
                        {
                            "series_id": series,
                            "metadata": project(d.association_for(series)),
                            "reason": None
                            if d.association_for(series)
                            else "ambiguous_or_not_reported",
                        }
                        for series in runtime.schedule.series
                    ],
                }
                for d in runtime.favorites.selected(reference.drivers)
                if reference_health("drivers") == "available"
            ],
            "tracks": [
                project(t)
                for i, t in reference.tracks.items()
                if i in tracks and reference_health("tracks") == "available"
            ],
        },
        "upcoming": [
            {
                **race_summary(r),
                "sessions": project(compact_sessions(r)),
                "sessions_complete": len(r.sessions) <= 4,
            }
            for r in compact
        ],
        "navigation": [
            {
                "series_id": series,
                "seasons": sorted(
                    {
                        r.season
                        for r in runtime.schedule.usable_races(series)
                        if r.season is not None
                    }
                ),
                "race_count": len(runtime.schedule.usable_races(series)),
                "unknown_start_count": sum(
                    r.start_time is None for r in runtime.schedule.usable_races(series)
                ),
                "failed_seasons": sorted(
                    runtime.schedule.data.failed_seasons.get(series, ())
                ),
            }
            for series in runtime.schedule.series
        ],
        "upcoming_complete": len(compact) == len(upcoming),
        "next_activity": {
            "start_time": project(next_activity[0]),
            "race": race_summary(next_activity[1]),
            "session": project(next_activity[2]),
        }
        if next_activity
        else None,
        "next_activity_reason": None if next_activity else "no_known_future_instant",
        "supported_sessions": ["practice", "qualifying", "race"],
        "capabilities": {
            "history_datasets": [
                "weekend",
                "laps",
                "notes",
                "loop",
                "averages",
                "pits",
                "stages",
            ],
            "analytics_contract_version": 1,
            "access": "administrator",
            "live_push": True,
        },
        "provider": entry.options.get(
            CONF_PROVIDER, entry.data.get(CONF_PROVIDER, PROVIDER_DEMO)
        ),
        "source_state": [
            {
                "series_id": s,
                "live": runtime.live.view(s).health,
                "schedule": "unavailable"
                if s in runtime.schedule.data.failed_series
                or not runtime.schedule.last_update_success
                else "available",
            }
            for s in runtime.schedule.series
        ],
        "limitations": list(LIMITATIONS),
    }


def live(entry: NascarConfigEntry, series_id: int) -> dict[str, Any]:
    runtime = entry.runtime_data
    view = runtime.live.view(series_id)
    snap = view.snapshot
    board = view.leaderboard
    # Failed/stale data has identity and clock context, never current timing rows.
    identity: dict[str, Any] = (
        fields(snap, "series_id race_id run_id")
        if snap
        else {"series_id": series_id, "race_id": None, "run_id": None}
    )
    seasons = {
        r.season
        for r in runtime.schedule.usable_races(series_id)
        if snap and r.race_id == snap.race_id
    }
    identity["season"] = next(iter(seasons)) if len(seasons) == 1 else None
    identity["season_basis"] = (
        "cached_schedule" if identity["season"] else "not_reported"
    )
    drivers = []
    if board:
        for driver in board.drivers:
            row = fields(
                driver,
                (
                    "driver_id name car_number manufacturer position "
                    "starting_position laps_completed last_lap_time best_lap_time "
                    "last_lap_speed best_lap_speed average_speed gap status_code "
                    "is_on_track pits_failed"
                ),
            )
            row.update(
                {
                    "favorite": runtime.favorites.contains(driver.driver_id),
                    "running_status": driver.running_status,
                    "position_change": {
                        "value": driver.position_change,
                        "classification": "derived",
                        "method": "starting_position_minus_position",
                    },
                }
            )
            for name in ("pit_stops", "laps_led"):
                values = getattr(driver, name)
                row[name] = {
                    "records": project(values[:2]) if values is not None else None,
                    "total": len(values) if values is not None else None,
                    "complete": values is None or len(values) <= 2,
                    "detail_command": "live_driver",
                }
            drivers.append(row)
    scoring = {}
    for kind in ("pits", "stages", "points"):
        feed = runtime.scoring.feed(kind, series_id)
        values = getattr(feed, kind) if feed else None
        scoring[kind] = {
            "status": runtime.scoring.capability(kind, series_id),
            "provenance": project(feed.provenance) if feed else None,
            "classification": "provisional",
            "records": project(values[:2]) if values is not None else None,
            "total": len(values) if values is not None else None,
            "complete": values is None or len(values) <= 2,
            "detail_command": "live_scoring",
        }
    return {
        "identity": identity,
        "availability": view.health,
        "session_state": view.session_status,
        "observation_advancement": view.observation_state
        or ("no_session" if runtime.live.data is None else "not_assessed"),
        "source_updated_at": project(snap.source_updated_at) if snap else None,
        "stale": runtime.live.source_is_stale if snap else None,
        "session": {
            **fields(
                snap,
                (
                    "run_name status run_type_code flag flag_state_code lap "
                    "total_laps laps_remaining elapsed_seconds leaderboard_failed "
                    "stage_failed"
                ),
            ),
            "progress": view.session_status,
            "stage": project(snap.stage),
        }
        if snap and view.available
        else None,
        "leader_driver_id": str(board.leader.driver_id)
        if board and board.leader
        else None,
        "leaderboard": drivers if board else None,
        "reported_count": board.reported_count if board else None,
        "omitted_count": board.omitted_count if board else None,
        "scoring": scoring,
        "limitations": list(LIMITATIONS),
    }
