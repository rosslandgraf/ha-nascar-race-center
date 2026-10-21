"""Bounded integration diagnostics with no source payloads or credentials."""

from typing import Any

from homeassistant.core import HomeAssistant

from . import NascarConfigEntry
from .const import CONF_PROVIDER, PROVIDER_DEMO
from .provider import CFProvider


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: NascarConfigEntry
) -> dict[str, Any]:
    """Report normalized availability while excluding URLs, headers and raw data."""
    schedule = entry.runtime_data.schedule
    live = entry.runtime_data.live
    reference = entry.runtime_data.reference
    snapshot = live.data
    return {
        "provider": entry.options.get(
            CONF_PROVIDER, entry.data.get(CONF_PROVIDER, PROVIDER_DEMO)
        ),
        "selected_series": list(schedule.series),
        "schedule": {
            "last_update_success": schedule.last_update_success,
            "failed_series": sorted(schedule.data.failed_series)
            if schedule.last_update_success
            else list(schedule.series),
            "failed_seasons": {
                str(key): sorted(years)
                for key, years in schedule.data.failed_seasons.items()
                if years
            },
            "race_counts": {
                str(key): len(value) for key, value in schedule.data.races.items()
            },
            "last_successful_updates": {
                str(key): value.isoformat()
                for key, value in schedule.data.updated_at.items()
            },
            "unknown_start_time_counts": {
                str(key): sum(race.start_time is None for race in races)
                for key, races in schedule.data.races.items()
            },
            "timestamp_policy": "explicit_offset_required",
            "session_detail_failures": [
                {"season": year, "series_id": series_id}
                for year, series_id in sorted(
                    entry.runtime_data.provider.schedule_details_failed
                )
            ]
            if isinstance(entry.runtime_data.provider, CFProvider)
            else [],
            "invalid_session_list_counts": {
                str(key): sum(race.sessions_failed for race in races)
                for key, races in schedule.data.races.items()
            },
            "last_http_status": schedule.last_error_status,
            "session_counts": {
                str(key): sum(len(race.sessions) for race in races)
                for key, races in schedule.data.races.items()
            },
            "unknown_session_start_counts": {
                str(key): sum(
                    session.start_time is None
                    for race in races
                    for session in race.sessions
                )
                for key, races in schedule.data.races.items()
            },
        },
        "reference": {
            "failed_feeds": sorted(reference.data.failed_feeds),
            "driver_count": len(reference.data.drivers),
            "track_count": len(reference.data.tracks),
            "last_successful_updates": {
                key: value.isoformat()
                for key, value in reference.data.updated_at.items()
            },
            "last_http_status": reference.last_error_status,
            "favorite_count": len(entry.runtime_data.favorites.ids),
        },
        "live": {
            "last_update_success": live.last_update_success,
            "last_successful_update": live.last_successful_update.isoformat()
            if live.last_successful_update
            else None,
            "last_http_status": live.last_error_status,
            "rate_limited": live.last_error_status == 429,
            "source_stale": live.source_is_stale,
            "poll_interval_seconds": live.update_interval.total_seconds()
            if live.update_interval
            else None,
            "series_id": snapshot.series_id if snapshot else None,
            "race_id": snapshot.race_id if snapshot else None,
            "source_updated_at": snapshot.source_updated_at.isoformat()
            if snapshot and snapshot.source_updated_at
            else None,
            "run_id": snapshot.run_id if snapshot else None,
            "session_progress": live.view(snapshot.series_id).session_status
            if snapshot
            else None,
            "timing": {
                "status": "invalid"
                if snapshot.leaderboard_failed
                else "reported"
                if snapshot.leaderboard is not None
                else "unknown",
                "normalized_count": len(snapshot.leaderboard.drivers)
                if snapshot.leaderboard is not None
                else None,
                "reported_count": snapshot.leaderboard.reported_count
                if snapshot.leaderboard is not None
                else None,
                "omitted_count": snapshot.leaderboard.omitted_count
                if snapshot.leaderboard is not None
                else None,
                "field_counts": {
                    key: sum(
                        getattr(driver, key) is not None
                        for driver in snapshot.leaderboard.drivers
                    )
                    for key in (
                        "position",
                        "last_lap_time",
                        "best_lap_time",
                        "gap",
                        "last_lap_speed",
                        "best_lap_speed",
                        "average_speed",
                        "laps_completed",
                        "laps_led",
                        "status_code",
                    )
                }
                if snapshot.leaderboard is not None
                else {},
            }
            if snapshot
            else {},
            "timestamp_policy": "explicit_offset_required",
            "field_availability": {
                key: getattr(snapshot, key) is not None
                for key in ("status", "flag", "lap", "source_updated_at")
            }
            if snapshot
            else {},
        },
    }
