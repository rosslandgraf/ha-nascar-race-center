"""Compact favorite-driver reference metadata; no premature live race metrics."""

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import NascarConfigEntry
from .const import (
    CONF_PROVIDER,
    DOMAIN,
    PROVIDER_DEMO,
    REFERENCE_STALE_AFTER,
)
from .reference import Driver
from .reference_coordinator import ReferenceCoordinator


async def async_setup_favorites(
    hass: HomeAssistant,
    entry: NascarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one stable metadata entity per selection, even during an outage."""
    async_add_entities(
        NascarFavoriteDriverSensor(entry, driver_id)
        for driver_id in entry.runtime_data.favorites.ids
    )


class NascarFavoriteDriverSensor(CoordinatorEntity[ReferenceCoordinator], SensorEntity):
    """Resolve reference metadata by NASCAR ID independently of series changes."""

    _attr_has_entity_name = True
    _attr_translation_key = "driver_metadata"
    _attr_icon = "mdi:account-star"

    def __init__(self, entry: NascarConfigEntry, driver_id: int) -> None:
        """Numbers and team/name changes never change the persisted entity ID."""
        super().__init__(entry.runtime_data.reference)
        self.driver_id = driver_id
        self.registry = entry.runtime_data.favorites
        self._attr_unique_id = f"{entry.entry_id}_driver_{driver_id}_metadata"
        provider = entry.options.get(
            CONF_PROVIDER, entry.data.get(CONF_PROVIDER, PROVIDER_DEMO)
        )
        suffix = " (Demo)" if provider == PROVIDER_DEMO else ""
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_driver_{driver_id}")},
            name=f"NASCAR driver {driver_id}{suffix}",
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="NASCAR Race Center community project",
            model="Favorite driver reference",
        )

    @property
    def driver(self) -> Driver | None:
        """Look up the latest normalized model while keeping the selected ID."""
        return self.registry.get(self.driver_id, self.coordinator.data.drivers)

    @property
    def available(self) -> bool:
        """A failed/stale directory cannot present old metadata as current."""
        data = self.coordinator.data
        updated_at = data.updated_at.get("drivers")
        return (
            super().available
            and "drivers" not in data.failed_feeds
            and updated_at is not None
            and dt_util.utcnow() - updated_at <= REFERENCE_STALE_AFTER
            and self.driver is not None
        )

    @property
    def native_value(self) -> str | None:
        """Expose the known name, never a manufactured position or roster state."""
        return self.driver.name if self.driver is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Keep attributes bounded; full reference models stay in runtime data."""
        driver = self.driver
        if driver is None:
            return {"driver_id": self.driver_id}
        return {
            "driver_id": driver.driver_id,
            "series_ids": list(driver.series_ids),
            "car_number": driver.car_number,
            "team": driver.team,
            "manufacturer": driver.manufacturer,
            "series_metadata": [
                {
                    "series_id": series_id,
                    "car_number": association.car_number,
                    "team": association.team,
                    "manufacturer": association.manufacturer,
                }
                for series_id in (1, 2, 3)
                if (association := driver.association_for(series_id)) is not None
            ],
        }
