"""Source freshness diagnostics."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NascarConfigEntry
from .entity import LiveEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NascarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Expose source staleness without guessing when no timestamp is published."""
    async_add_entities(
        NascarFeedStaleSensor(entry, series_id)
        for series_id in entry.runtime_data.schedule.series
    )


class NascarFeedStaleSensor(LiveEntity, BinarySensorEntity):
    """The source can be old even after a successful HTTP refresh."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "feed_stale"

    def __init__(self, entry: NascarConfigEntry, series_id: int) -> None:
        """Initialize the stable series-scoped diagnostic."""
        super().__init__(entry, series_id, "feed_stale")

    @property
    def is_on(self) -> bool | None:
        """A missing timestamp is unknown, never a healthy false reading."""
        return self.coordinator.source_is_stale if self.series_is_active else None
