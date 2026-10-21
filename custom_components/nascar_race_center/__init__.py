"""NASCAR Race Center Home Assistant integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store

from .analytics_runtime import AnalyticsService
from .const import (
    CONF_APPROACHING_INTERVAL,
    CONF_DATA_USE_AUTHORIZED,
    CONF_FAVORITE_DRIVERS,
    CONF_LIVE_INTERVAL,
    CONF_POLLING_POLICY,
    CONF_PROVIDER,
    CONF_SERIES,
    DEFAULT_APPROACHING_INTERVAL,
    DEFAULT_LIVE_INTERVAL,
    DEFAULT_POLLING_POLICY,
    DEFAULT_SERIES,
    DOMAIN,
    FAVORITE_LIVE_METRICS,
    FAVORITE_SCORING_METRICS,
    MAX_LIVE_INTERVAL,
    MIN_LIVE_INTERVAL,
    PLATFORMS,
    PROVIDER_CF,
    PROVIDER_DEMO,
)
from .coordinator import LiveCoordinator, ScheduleCoordinator
from .event_runtime import EventRuntime
from .events import EventPreferences
from .favorites import FavoriteDriverRegistry
from .history import HistoryService
from .history_provider import CFHistoryProvider, DemoHistoryProvider
from .polling_storage import LiveRequestGuard
from .provider import CFProvider, DemoProvider, RaceProvider
from .reference_coordinator import ReferenceCoordinator
from .reference_provider import (
    CFReferenceProvider,
    DemoReferenceProvider,
    ReferenceProvider,
)
from .scoring_coordinator import ScoringCoordinator
from .scoring_provider import CFScoringProvider, DemoScoringProvider, ScoringProvider


@dataclass(frozen=True)
class RuntimeData:
    """Entry-owned provider and coordinated state."""

    provider: RaceProvider
    schedule: ScheduleCoordinator
    live: LiveCoordinator
    reference: ReferenceCoordinator
    favorites: FavoriteDriverRegistry
    scoring: ScoringCoordinator
    events: EventRuntime
    history: HistoryService
    analytics: AnalyticsService


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
    polling_policy = options.get(CONF_POLLING_POLICY, DEFAULT_POLLING_POLICY)
    approaching_interval = options.get(
        CONF_APPROACHING_INTERVAL, DEFAULT_APPROACHING_INTERVAL
    )
    if (
        polling_policy not in ("conservative", "adaptive")
        or type(approaching_interval) is not int
        or not 30 <= approaching_interval <= 60
    ):
        raise ConfigEntryError(
            "Select a valid live polling policy and approaching interval"
        )
    try:
        favorites = FavoriteDriverRegistry(options.get(CONF_FAVORITE_DRIVERS, []))
    except ValueError as err:
        raise ConfigEntryError("Select valid NASCAR driver IDs") from err
    try:
        event_preferences = EventPreferences.from_options(options, favorites.ids)
    except ValueError as err:
        raise ConfigEntryError("Select valid racing event settings") from err
    provider: RaceProvider
    reference_provider: ReferenceProvider
    scoring_provider: ScoringProvider
    if provider_name == PROVIDER_CF:
        previous = hass.data.get(DOMAIN, {}).get(entry.entry_id)
        if isinstance(previous, CFProvider):
            # Keep the shared response cache/cooldowns through a normal reload.
            # A real restart restores only the compact request reservation.
            cf_provider = previous
        else:
            cf_provider = CFProvider(async_get_clientsession(hass))
            guard = LiveRequestGuard(hass, entry.entry_id)
            await guard.async_load()
            cf_provider.api.live_guard = guard
            hass.data.setdefault(DOMAIN, {})[entry.entry_id] = cf_provider
        provider = cf_provider
        reference_provider = CFReferenceProvider(cf_provider.api)
        scoring_provider = CFScoringProvider(cf_provider.api)
    else:
        provider = DemoProvider()
        reference_provider = DemoReferenceProvider()
        scoring_provider = DemoScoringProvider()
    schedule = ScheduleCoordinator(hass, entry, provider, series)
    live = LiveCoordinator(
        hass,
        entry,
        provider,
        schedule,
        live_interval,
        polling_policy=polling_policy,
        approaching_interval=approaching_interval,
    )
    reference = ReferenceCoordinator(hass, entry, reference_provider)
    scoring = ScoringCoordinator(hass, entry, scoring_provider, live)
    events = EventRuntime(hass, entry, live, schedule, event_preferences, provider_name)
    history = HistoryService(
        CFHistoryProvider(cf_provider.api)
        if provider_name == PROVIDER_CF
        else DemoHistoryProvider(),
        series,
    )
    # Register before first refresh so failed/cancelled setup drains requests too.
    entry.async_on_unload(history.async_close)
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, history.async_close)
    )
    analytics = AnalyticsService(hass, history)
    entry.async_on_unload(analytics.async_close)
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, analytics.async_close)
    )
    entry.runtime_data = RuntimeData(
        provider=provider,
        schedule=schedule,
        live=live,
        reference=reference,
        favorites=favorites,
        scoring=scoring,
        events=events,
        history=history,
        analytics=analytics,
    )
    # DataUpdateCoordinator registers each async_shutdown override with
    # entry.async_on_unload during construction, before either first refresh.
    # HA awaits these callbacks on unload, reload and failed/cancelled setup.
    # Keep the same provider and its retry deadlines through startup outages.
    # A first-refresh setup failure would recreate it on HA's faster setup retry.
    await schedule.async_refresh()
    await live.async_refresh()
    await reference.async_refresh()
    await scoring.async_refresh()
    _remove_deselected_favorite_entities(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await events.async_start()
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


def _remove_deselected_favorite_entities(
    hass: HomeAssistant, entry: NascarConfigEntry
) -> None:
    """Remove only recognized favorite metrics for explicitly removed IDs."""
    registry = er.async_get(hass)
    selected = {
        f"{entry.entry_id}_driver_{driver_id}_metadata"
        for driver_id in entry.runtime_data.favorites.ids
    }
    selected.update(
        f"{entry.entry_id}_driver_{driver_id}_live_{key}"
        for driver_id in entry.runtime_data.favorites.ids
        for key in FAVORITE_LIVE_METRICS
    )
    selected.update(
        f"{entry.entry_id}_driver_{driver_id}_scoring_{key}"
        for driver_id in entry.runtime_data.favorites.ids
        for key in FAVORITE_SCORING_METRICS
    )
    suffixes = (
        "_metadata",
        *(f"_live_{key}" for key in FAVORITE_LIVE_METRICS),
        *(f"_scoring_{key}" for key in FAVORITE_SCORING_METRICS),
    )
    prefix = f"{entry.entry_id}_driver_"
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if (
            entity.platform == DOMAIN
            and entity.domain == "sensor"
            and entity.unique_id.startswith(prefix)
            and entity.unique_id.endswith(suffixes)
            and entity.unique_id not in selected
        ):
            registry.async_remove(entity.entity_id)
    devices = dr.async_get(hass)
    selected_devices = {
        (DOMAIN, f"{entry.entry_id}_driver_{driver_id}")
        for driver_id in entry.runtime_data.favorites.ids
    }
    for device in dr.async_entries_for_config_entry(devices, entry.entry_id):
        if (
            any(
                domain == DOMAIN and identifier.startswith(prefix)
                for domain, identifier in device.identifiers
            )
            and not (device.identifiers & selected_devices)
            and not er.async_entries_for_device(registry, device.id)
        ):
            devices.async_remove_device(device.id)


async def _async_options_updated(hass: HomeAssistant, entry: NascarConfigEntry) -> None:
    """Reload after a UI update without leaving old polling loops active."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: NascarConfigEntry) -> bool:
    """Unload platforms; HA then awaits the entry-owned coordinator shutdowns.

    If platform unload fails, keep the coordinators running for the loaded entry.
    The shared aiohttp session belongs to HA and must not be closed here.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: NascarConfigEntry) -> None:
    """Removing the installation removes its compact event ledger too."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    await Store(hass, 1, f"{DOMAIN}.{entry.entry_id}.events").async_remove()
    await Store(hass, 1, f"{DOMAIN}.{entry.entry_id}.live_polling").async_remove()
