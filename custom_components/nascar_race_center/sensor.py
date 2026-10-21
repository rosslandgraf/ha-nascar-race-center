"""Small, stable schedule and race-state entities."""

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NascarConfigEntry
from .const import FAVORITE_LIVE_METRICS, FAVORITE_SCORING_METRICS
from .driver_sensor import async_setup_favorites
from .entity import LiveEntity, ScheduleEntity
from .live_driver_sensor import NascarFavoriteLiveSensor
from .scoring_provider import SCORING_KINDS
from .scoring_sensor import (
    NascarCurrentStageSensor,
    NascarFavoriteScoringSensor,
    NascarRaceScoringSensor,
    NascarScoringCapabilitySensor,
)


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
                "session_status",
                "leader",
                "total_laps",
                "laps_remaining",
                "field_size",
            )
        )
        entities.append(NascarCurrentStageSensor(entry, series_id))
        entities.extend(
            NascarRaceScoringSensor(entry, series_id, key)
            for key in ("scored_stages", "championship_leader")
        )
        entities.extend(
            NascarScoringCapabilitySensor(entry, series_id, kind)
            for kind in SCORING_KINDS
        )
    entities.extend(
        NascarFavoriteScoringSensor(entry, driver_id, key)
        for driver_id in entry.runtime_data.favorites.ids
        for key in FAVORITE_SCORING_METRICS
    )
    entities.extend(
        NascarFavoriteLiveSensor(entry, driver_id, key)
        for driver_id in entry.runtime_data.favorites.ids
        for key in FAVORITE_LIVE_METRICS
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

    _unrecorded_attributes = frozenset({"source_updated_at"})

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
        if key == "field_size":
            self._attr_entity_registry_enabled_default = False
        if key in {"current_lap", "total_laps", "laps_remaining"}:
            self._attr_icon = "mdi:counter"
        if key == "flag":
            self._attr_icon = "mdi:flag-checkered"

    async def async_added_to_hass(self) -> None:
        """Keep legacy source-time context without timestamp-only state writes."""
        await super().async_added_to_hass()
        self._last_sample = self._sample_signature()

    def _sample_signature(
        self,
    ) -> tuple[bool, str | int | datetime | None, dict[str, Any]]:
        attributes = dict(self.extra_state_attributes or {})
        attributes.pop("source_updated_at", None)
        return self.available, self.native_value, attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Write only changed values, availability or compact session context.

        source_updated_at remains the timestamp of this sensor's last meaningful
        sample. Diagnostics provide the latest source/transport observation.
        Recorder's unrecorded attributes alone do not suppress redundant rows.
        """
        sample = self._sample_signature()
        if sample != self._last_sample:
            self._last_sample = sample
            super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        """Health remains visible when transport or the source is stale."""
        if self.key in {"feed_status", "last_successful_update"}:
            return True
        if self.key in {"race_status", "session_status"}:
            return super().available
        if self.key in {"leader", "field_size", "total_laps", "laps_remaining"}:
            if not self.coordinator.view(self.series_id).available:
                return False
        snapshot = self.coordinator.data
        if self.key in {"leader", "field_size"} and snapshot is not None:
            if snapshot.leaderboard_failed:
                return False
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
        view = self.coordinator.view(self.series_id)
        if self.key == "feed_status":
            return view.health
        if self.key == "session_status":
            return view.session_status
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
        board = view.leaderboard
        if self.key == "leader":
            return board.leader.driver_id if board and board.leader else None
        if self.key == "field_size":
            return len(board.drivers) if board is not None else None
        return {
            "total_laps": snapshot.total_laps,
            "laps_remaining": snapshot.laps_remaining,
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
        if self.key == "leader":
            board = self.coordinator.view(self.series_id).leaderboard
            leader = board.leader if board else None
            return {
                "series_id": snapshot.series_id,
                "race_id": snapshot.race_id,
                "run_id": snapshot.run_id,
                "driver_name": leader.name if leader else None,
                "car_number": leader.car_number if leader else None,
            }
        if self.key in {"session_status", "total_laps", "laps_remaining", "field_size"}:
            return {
                "series_id": snapshot.series_id,
                "race_id": snapshot.race_id,
                "run_id": snapshot.run_id,
            }
        return {
            "series_id": snapshot.series_id,
            "race_id": snapshot.race_id,
            "source_updated_at": snapshot.source_updated_at,
        }
