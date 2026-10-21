"""Selected-driver timing from the single reported, monitored live series."""

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NascarConfigEntry
from .coordinator import LiveCoordinator
from .driver_sensor import favorite_device
from .timing import LiveDriver


class NascarFavoriteLiveSensor(CoordinatorEntity[LiveCoordinator], SensorEntity):
    """Stable per-driver metrics across series, cars, names, races and runs.

    There is one current global source, so series context accompanies each value.
    No per-field/per-series entity multiplication or reference-feed dependency.
    """

    _attr_has_entity_name = True

    def __init__(self, entry: NascarConfigEntry, driver_id: int, key: str) -> None:
        """Enable only position by default to bound normal Recorder traffic."""
        super().__init__(entry.runtime_data.live)
        self.driver_id = driver_id
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_driver_{driver_id}_live_{key}"
        self._attr_device_info = favorite_device(entry, driver_id)
        self._attr_translation_key = f"driver_live_{key}"
        self._attr_entity_registry_enabled_default = key == "position"
        self._attr_icon = "mdi:go-kart"
        if key in {"last_lap", "best_lap"}:
            self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
            self._attr_suggested_display_precision = 3
        # delta has no verified unit/negative-value semantics; do not label it s.

    @property
    def driver(self) -> LiveDriver | None:
        """Never reuse scoring from an unmonitored series or another driver ID."""
        snapshot = self.coordinator.data
        if snapshot is None:
            return None
        return self.coordinator.view(snapshot.series_id).driver(self.driver_id)

    @property
    def available(self) -> bool:
        """A missing field entry differs from an entry with an unknown metric."""
        return super().available and self.driver is not None

    @property
    def native_value(self) -> str | int | float | None:
        """Missing values remain unknown, including unmapped running codes."""
        driver = self.driver
        if driver is None:
            return None
        return {
            "position": driver.position,
            "last_lap": driver.last_lap_time,
            "best_lap": driver.best_lap_time,
            "gap": driver.gap,
            "running_status": driver.running_status,
            "position_change": driver.position_change,
        }[self.key]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Only compact identity; no changing timestamps or full competitor rows."""
        snapshot = self.coordinator.data
        if self.driver is None or snapshot is None:
            return {"driver_id": self.driver_id}
        return {
            "driver_id": self.driver_id,
            "series_id": snapshot.series_id,
            "race_id": snapshot.race_id,
            "run_id": snapshot.run_id,
        }
