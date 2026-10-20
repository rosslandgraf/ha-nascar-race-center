"""Small, stable schedule and race-state entities."""

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NascarConfigEntry
from .driver_sensor import async_setup_favorites
from .entity import LiveEntity, ScheduleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NascarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add essential metrics without storing entire feeds in Recorder."""
    entities: list[SensorEntity] = []
    for series_id in entry.runtime_data.schedule.series:
        entities.extend(
            NascarScheduleSensor(entry, series_id, key)
            for key in ("next_race", "next_race_start", "scheduled_races")
        )
        entities.extend(
            NascarLiveSensor(entry, series_id, key)
            for key in (
                "race_status",
                "flag",
                "current_lap",
                "feed_status",
                "last_successful_update",
            )
        )
    async_add_entities(entities)
    await async_setup_favorites(hass, entry, async_add_entities)


class NascarScheduleSensor(ScheduleEntity, SensorEntity):
    """Expose a next race and an aggregate schedule count."""

    def __init__(self, entry: NascarConfigEntry, series_id: int, key: str) -> None:
        """Set metric metadata and stable identity."""
        super().__init__(entry, series_id, key)
        self.key = key
        self._attr_translation_key = key
        if key == "next_race_start":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        if key == "scheduled_races":
            self._attr_icon = "mdi:calendar"

    @property
    def native_value(self) -> str | int | datetime | None:
        """Unknown dates remain unknown rather than a fabricated countdown."""
        if self.key == "scheduled_races":
            return len(self.coordinator.usable_races(self.series_id))
        race = self.coordinator.next_race(self.series_id)
        if race is None:
            return None
        if self.key == "next_race_start":
            return race.start_time
        return race.name

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Keep only the next race identity and track, never a full schedule."""
        if self.key == "scheduled_races":
            return {
                "unknown_start_times": sum(
                    race.start_time is None
                    for race in self.coordinator.usable_races(self.series_id)
                )
            }
        race = self.coordinator.next_race(self.series_id)
        if race is None:
            return None
        return {
            "race_id": race.race_id,
            "series_id": race.series_id,
            "track": race.track,
        }


class NascarLiveSensor(LiveEntity, SensorEntity):
    """Expose current-series data and explicit transport/source health."""

    def __init__(self, entry: NascarConfigEntry, series_id: int, key: str) -> None:
        """Set metadata without assuming optional feed fields are present."""
        super().__init__(entry, series_id, key)
        self.key = key
        self._attr_translation_key = key
        if key in {"feed_status", "last_successful_update"}:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if key == "last_successful_update":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
            self._attr_entity_registry_enabled_default = False
        if key == "current_lap":
            self._attr_icon = "mdi:counter"
        if key == "flag":
            self._attr_icon = "mdi:flag-checkered"

    @property
    def available(self) -> bool:
        """Health remains visible when transport or the source is stale."""
        if self.key in {"feed_status", "last_successful_update"}:
            return True
        if self.key == "race_status":
            return super().available
        return (
            super().available
            and self.series_is_active
            and self.coordinator.source_is_stale is not True
        )

    @property
    def native_value(self) -> str | int | datetime | None:
        """No active session is different from a broken or old feed."""
        if self.key == "last_successful_update":
            return self.coordinator.last_successful_update
        if self.key == "feed_status":
            if not self.coordinator.last_update_success:
                return (
                    "denied"
                    if self.coordinator.last_error_status in {401, 403}
                    else "offline"
                )
            if not self.series_is_active:
                return (
                    "not_reported"
                    if self.coordinator.data is not None
                    else "no_active_session"
                )
            if self.coordinator.source_is_stale is None:
                return "freshness_unknown"
            return "stale" if self.coordinator.source_is_stale else "ok"
        if not self.series_is_active:
            if self.key == "race_status":
                return (
                    "not_reported"
                    if self.coordinator.data is not None
                    else "no_active_session"
                )
            return None
        if self.coordinator.source_is_stale:
            return "stale" if self.key == "race_status" else None
        snapshot = self.coordinator.data
        if snapshot is None:
            return None
        return {
            "race_status": snapshot.status,
            "flag": snapshot.flag,
            "current_lap": snapshot.lap,
        }[self.key]

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Include bounded context only for the corresponding reported series."""
        snapshot = self.coordinator.data
        if not self.series_is_active or snapshot is None:
            return None
        return {
            "series_id": snapshot.series_id,
            "race_id": snapshot.race_id,
            "source_updated_at": snapshot.source_updated_at,
        }
