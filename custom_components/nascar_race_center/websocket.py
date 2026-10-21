"""Official authenticated Home Assistant WebSocket extension, dashboard API v1."""

from typing import Any

import probatio as vol
from homeassistant.components import websocket_api
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.components.websocket_api.decorators import websocket_command
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .dashboard import API_VERSION, authorized
from .dashboard_pages import MAX_PAGE_RECORDS

PREFIX = f"{DOMAIN}/dashboard/"
REGISTERED = f"{DOMAIN}.dashboard_registered"


def integer(low: int, high: int) -> vol.All[Any]:
    """Reject Boolean and coerced/string selections before any service call."""

    def exact(value: Any) -> int:
        if type(value) is not int:
            raise vol.Invalid("Expected an integer")
        return value

    return vol.All(exact, vol.Range(min=low, max=high))


def distinct(values: list[Any]) -> list[Any]:
    if len(set(values)) != len(values):
        raise vol.Invalid("Selections must be distinct")
    return values


def async_register(hass: HomeAssistant) -> None:
    """Register once per HA instance; closures never retain a config-entry runtime."""
    if hass.data.get(REGISTERED):
        return
    positive = integer(1, 10**10)
    season = integer(1948, 9999)
    common: dict[Any, Any] = {
        vol.Required("entry_id"): vol.All(str, vol.Length(min=1, max=128)),
        vol.Required("api_version"): integer(API_VERSION, API_VERSION),
    }
    series: dict[Any, Any] = {vol.Required("series_id"): vol.All(integer(1, 3))}
    pagination: dict[Any, Any] = {
        vol.Optional("offset", default=0): integer(0, 1_000_000),
        vol.Optional("limit", default=100): integer(1, MAX_PAGE_RECORDS),
        vol.Optional("snapshot"): vol.Match(r"^[0-9a-f]{64}$"),
    }
    history: dict[Any, Any] = {
        **series,
        **pagination,
        vol.Required("season"): season,
        vol.Required("race_id"): positive,
        vol.Required("datasets"): vol.All(
            vol.Length(min=1, max=7),
            [
                vol.In(
                    ("weekend", "laps", "notes", "loop", "averages", "pits", "stages")
                )
            ],
            distinct,
        ),
    }
    commands: dict[str, dict[Any, Any]] = {
        "bootstrap": {},
        "schedule": {
            **series,
            **pagination,
            vol.Optional("season"): season,
            vol.Optional("race_id"): positive,
        },
        "live": series,
        "subscribe_live": series,
        "live_driver": {
            **series,
            **pagination,
            vol.Required("driver_id"): integer(1, 10**20),
            vol.Required("collection"): vol.In(("pit_stops", "laps_led")),
        },
        "live_scoring": {
            **series,
            **pagination,
            vol.Required("collection"): vol.In(("pits", "stages", "points")),
        },
        "history": history,
        "analytics": {
            **history,
            vol.Required("driver_ids"): vol.All(
                vol.Length(min=1, max=8), [positive], distinct
            ),
            vol.Required("first_lap"): integer(0, 10**10),
            vol.Required("last_lap"): integer(0, 10**10),
            vol.Required("windows"): vol.All(
                vol.Length(max=6),
                [vol.All(integer(5, 30), vol.In((5, 10, 15, 20, 25, 30)))],
                distinct,
            ),
            vol.Required("time_basis"): vol.In(
                ("all_available", "overlapping_valid_laps")
            ),
        },
    }
    for command, parameters in commands.items():
        _register_command(hass, command, {**common, **parameters})
    hass.data[REGISTERED] = True


def _register_command(
    hass: HomeAssistant, command: str, parameters: dict[Any, Any]
) -> None:
    @websocket_command({"type": PREFIX + command, **parameters})
    @callback
    def handle(
        hass: HomeAssistant,
        connection: ActiveConnection,
        msg: dict[str, Any],
    ) -> None:
        if not authorized(connection):
            connection.send_error(
                msg["id"], "unauthorized", "Administrator access required"
            )
            return
        entry = hass.config_entries.async_get_entry(msg["entry_id"])
        if (
            entry is None
            or entry.domain != DOMAIN
            or entry.state is not ConfigEntryState.LOADED
        ):
            connection.send_error(
                msg["id"],
                "entry_unavailable",
                "NASCAR configuration entry is not loaded",
            )
            return
        runtime = entry.runtime_data.dashboard
        if (
            "series_id" in msg
            and msg["series_id"] not in entry.runtime_data.schedule.series
        ):
            connection.send_error(
                msg["id"], "invalid_selection", "Series is not monitored by this entry"
            )
            return
        if error := runtime.admit(connection):
            connection.send_error(
                msg["id"],
                error,
                "Dashboard unavailable or request window exhausted; "
                "retry after 10 seconds",
            )
            return
        if command == "subscribe_live":
            runtime.subscribe(connection, msg)
        else:
            runtime.request(connection, msg)

    websocket_api.async_register_command(hass, handle)
