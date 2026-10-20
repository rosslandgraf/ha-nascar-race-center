"""NASCAR Race Center Home Assistant integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_LIVE_INTERVAL,
    CONF_PROVIDER,
    CONF_SERIES,
    DEFAULT_LIVE_INTERVAL,
    DEFAULT_SERIES,
    MAX_LIVE_INTERVAL,
    MIN_LIVE_INTERVAL,
    PLATFORMS,
    PROVIDER_CF,
    PROVIDER_DEMO,
)
from .coordinator import LiveCoordinator, ScheduleCoordinator
from .provider import CFProvider, DemoProvider, RaceProvider


@dataclass(frozen=True)
class RuntimeData:
    """Entry-owned provider and coordinated state."""

    provider: RaceProvider
    schedule: ScheduleCoordinator
    live: LiveCoordinator


type NascarConfigEntry = ConfigEntry[RuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: NascarConfigEntry) -> bool:
    """Set up an offline demo or explicitly authorized anonymous CF provider."""
    options = {**entry.data, **entry.options}
    provider_name = options.get(CONF_PROVIDER, PROVIDER_DEMO)
    if (
        provider_name == PROVIDER_CF
        and options.get(CONF_DATA_USE_AUTHORIZED) is not True
    ):
        raise ConfigEntryError("NASCAR CF data-use authorization is required")
    if not isinstance(provider_name, str) or provider_name not in {
        PROVIDER_CF,
        PROVIDER_DEMO,
    }:
        raise ConfigEntryError("Unsupported NASCAR Race Center provider")
    raw_series = options.get(CONF_SERIES, DEFAULT_SERIES)
    if not isinstance(raw_series, (list, tuple)) or any(
        isinstance(value, bool) for value in raw_series
    ):
        raise ConfigEntryError("Select supported NASCAR series IDs")
    try:
        series = tuple(sorted({int(value) for value in raw_series}))
    except (TypeError, ValueError) as err:
        raise ConfigEntryError("Select supported NASCAR series IDs") from err
    if not series or any(value not in (1, 2, 3) for value in series):
        raise ConfigEntryError("Select at least one supported NASCAR series")
    live_interval = options.get(CONF_LIVE_INTERVAL, DEFAULT_LIVE_INTERVAL)
    if (
        not isinstance(live_interval, int)
        or isinstance(live_interval, bool)
        or not MIN_LIVE_INTERVAL <= live_interval <= MAX_LIVE_INTERVAL
    ):
        raise ConfigEntryError("Live polling interval must be 300 to 3600 seconds")
    provider: RaceProvider = (
        CFProvider(async_get_clientsession(hass))
        if provider_name == PROVIDER_CF
        else DemoProvider()
    )
    schedule = ScheduleCoordinator(hass, entry, provider, series)
    live = LiveCoordinator(hass, entry, provider, schedule, live_interval)
    entry.runtime_data = RuntimeData(provider=provider, schedule=schedule, live=live)
    # Keep the same provider and its retry deadlines through startup outages.
    # A first-refresh setup failure would recreate it on HA's faster setup retry.
    await schedule.async_refresh()
    await live.async_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: NascarConfigEntry) -> None:
    """Reload after a UI update without leaving old polling loops active."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: NascarConfigEntry) -> bool:
    """Unload platforms; coordinators stop when their entity listeners detach."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
