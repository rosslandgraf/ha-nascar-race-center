"""Shared series identity and availability rules."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import NascarConfigEntry
from .const import (
    CONF_PROVIDER,
    DOMAIN,
    PROVIDER_DEMO,
    SCHEDULE_STALE_AFTER,
    SERIES_NAMES,
)
from .coordinator import LiveCoordinator, ScheduleCoordinator


def series_device(entry: NascarConfigEntry, series_id: int) -> DeviceInfo:
    """Keep one stable service device per series across reloads and seasons."""
    provider = entry.options.get(
        CONF_PROVIDER, entry.data.get(CONF_PROVIDER, PROVIDER_DEMO)
    )
    suffix = " (Demo)" if provider == PROVIDER_DEMO else ""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_{series_id}")},
        name=f"{SERIES_NAMES[series_id]}{suffix}",
        entry_type=DeviceEntryType.SERVICE,
        manufacturer="NASCAR Race Center community project",
        model="Series race center",
    )


class ScheduleEntity(CoordinatorEntity[ScheduleCoordinator]):
    """Entity with independent per-series schedule availability."""

    _attr_has_entity_name = True

    def __init__(self, entry: NascarConfigEntry, series_id: int, key: str) -> None:
        """Identify this entity by stable series and metric IDs."""
        super().__init__(entry.runtime_data.schedule)
        self.series_id = series_id
        self._attr_unique_id = f"{entry.entry_id}_{series_id}_{key}"
        self._attr_device_info = series_device(entry, series_id)

    @property
    def available(self) -> bool:
        """Do not present a failed or long-expired series as current."""
        data = self.coordinator.data
        return (
            super().available
            and data is not None
            and self.series_id not in data.failed_series
            and self.series_id in data.updated_at
            and dt_util.utcnow() - data.updated_at[self.series_id]
            <= SCHEDULE_STALE_AFTER
        )


class LiveEntity(CoordinatorEntity[LiveCoordinator]):
    """Entity using a single global feed, filtered by the reported series."""

    _attr_has_entity_name = True

    def __init__(self, entry: NascarConfigEntry, series_id: int, key: str) -> None:
        """Never confuse a car number or current race name with series identity."""
        super().__init__(entry.runtime_data.live)
        self.series_id = series_id
        self._attr_unique_id = f"{entry.entry_id}_{series_id}_{key}"
        self._attr_device_info = series_device(entry, series_id)

    @property
    def series_is_active(self) -> bool:
        """The global live feed is authoritative only for its own series."""
        snapshot = self.coordinator.data
        return snapshot is not None and snapshot.series_id == self.series_id
