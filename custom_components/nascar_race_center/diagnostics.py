"""Bounded integration diagnostics with no source payloads or credentials."""

from typing import Any

from homeassistant.core import HomeAssistant

from . import NascarConfigEntry
from .const import CONF_PROVIDER, PROVIDER_DEMO


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: NascarConfigEntry
) -> dict[str, Any]:
    """Report normalized availability while excluding URLs, headers and raw data."""
    schedule = entry.runtime_data.schedule
    live = entry.runtime_data.live
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
            "last_http_status": schedule.last_error_status,
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
            "field_availability": {
                key: getattr(snapshot, key) is not None
                for key in ("status", "flag", "lap", "source_updated_at")
            }
            if snapshot
            else {},
        },
    }
