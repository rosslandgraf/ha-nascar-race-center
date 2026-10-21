"""Compact pit/stage/points projections; datasets stay in coordinator memory."""

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NascarConfigEntry
from .driver_sensor import favorite_device
from .entity import LiveEntity, series_device
from .scoring import latest_pit
from .scoring_coordinator import ScoringCoordinator
from .scoring_provider import ScoringKind


class NascarCurrentStageSensor(LiveEntity, SensorEntity):
    def __init__(self, entry: NascarConfigEntry, series_id: int) -> None:
        super().__init__(entry, series_id, "current_stage")
        self._attr_translation_key = "current_stage"
        self._attr_icon = "mdi:flag-checkered"

    @property
    def available(self) -> bool:
        snapshot = self.coordinator.view(self.series_id).snapshot
        return (
            self.coordinator.view(self.series_id).available
            and snapshot is not None
            and snapshot.status == "race"
            and snapshot.stage is not None
            and not snapshot.stage_failed
        )

    @property
    def native_value(self) -> int | None:
        snapshot = self.coordinator.view(self.series_id).snapshot
        return (
            snapshot.stage.number
            if self.available and snapshot and snapshot.stage
            else None
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        snapshot = self.coordinator.view(self.series_id).snapshot
        if not self.available or snapshot is None or snapshot.stage is None:
            return None
        return {
            "series_id": snapshot.series_id,
            "race_id": snapshot.race_id,
            "run_id": snapshot.run_id,
            "source": "live_feed_embedded",
            "finish_at_lap": snapshot.stage.finish_at_lap,
            "laps_in_stage": snapshot.stage.laps_in_stage,
        }


class NascarScoringCapabilitySensor(
    CoordinatorEntity[ScoringCoordinator], SensorEntity
):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, entry: NascarConfigEntry, series_id: int, kind: ScoringKind
    ) -> None:
        super().__init__(entry.runtime_data.scoring)
        self.series_id = series_id
        self.kind = kind
        self._attr_unique_id = f"{entry.entry_id}_{series_id}_{kind}_capability"
        self._attr_translation_key = f"{kind}_capability"
        self._attr_device_info = series_device(entry, series_id)

    @property
    def available(self) -> bool:
        return True

    @property
    def native_value(self) -> str:
        return self.coordinator.capability(self.kind, self.series_id)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        result: dict[str, Any] = {"classification": "provisional"}
        if self.kind == "pits":
            # The global standalone source can be unbound while embedded pits
            # are usable through the parent NASCAR driver and live context.
            view = self.coordinator.live.view(self.series_id)
            board = view.leaderboard
            result["embedded"] = (
                "available"
                if board
                and view.snapshot
                and view.snapshot.status == "race"
                and any(d.pit_stops is not None for d in board.drivers)
                else "not_reported"
            )
        return result


class NascarFavoriteScoringSensor(CoordinatorEntity[ScoringCoordinator], SensorEntity):
    """One opt-in summary per capability per favorite, independent of series count."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry: NascarConfigEntry, driver_id: int, key: str) -> None:
        super().__init__(entry.runtime_data.scoring)
        self.driver_id = driver_id
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_driver_{driver_id}_scoring_{key}"
        self._attr_translation_key = f"driver_scoring_{key}"
        self._attr_device_info = favorite_device(entry, driver_id)

    def _sample(self) -> tuple[int | None, dict[str, Any]] | None:
        live = self.coordinator.live
        snapshot = live.data
        if snapshot is None or snapshot.status != "race":
            return None
        view = live.view(snapshot.series_id)
        if not view.available:
            return None
        attrs: dict[str, Any] = {
            "driver_id": self.driver_id,
            "series_id": snapshot.series_id,
            "race_id": snapshot.race_id,
            "run_id": snapshot.run_id,
        }
        if self.key == "pit_lap":
            driver = view.driver(self.driver_id)
            if driver is None or driver.pits_failed or driver.pit_stops is None:
                return None
            pit = latest_pit(driver.pit_stops)
            attrs["source"] = "live_feed_embedded"
            if pit is None:
                return None, attrs
            attrs.update(
                leader_lap=pit.leader_lap,
                entry_time_reported=pit.entry_time,
                exit_time_reported=pit.exit_time,
                entry_position=pit.entry_position,
                exit_position=pit.exit_position,
                position_change=pit.position_change,
            )
            return pit.lap, attrs
        kind: ScoringKind = "stages" if self.key == "stage_position" else "points"
        feed = self.coordinator.feed(kind, snapshot.series_id)
        if feed is None:
            return None
        attrs["classification"] = feed.classification
        attrs["source"] = feed.provenance.endpoint
        if self.key == "stage_position":
            # Latest numbered reported result, without claiming completion or
            # summing incomplete stages. Stage numbers do not prove chronology.
            candidates = [
                stage for stage in feed.stages if stage.driver(self.driver_id)
            ]
            if not candidates:
                return None
            stage = max(candidates, key=lambda stage: stage.number)
            result = stage.driver(self.driver_id)
            assert result is not None
            attrs.update(stage_number=stage.number, stage_points=result.points)
            return result.position, attrs
        points = feed.driver_points(self.driver_id)
        if points is None:
            return None
        attrs.update(
            championship_points=points.points,
            race_points=points.race_points,
            bonus_points=points.bonus_points,
            delta_leader_reported=points.delta_leader,
            delta_next_reported=points.delta_next,
        )
        return points.position, attrs

    @property
    def available(self) -> bool:
        return self._sample() is not None

    @property
    def native_value(self) -> int | None:
        sample = self._sample()
        return sample[0] if sample else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        sample = self._sample()
        return sample[1] if sample else {"driver_id": self.driver_id}


class NascarRaceScoringSensor(CoordinatorEntity[ScoringCoordinator], SensorEntity):
    """Optional small race summaries, only for associated source observations."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry: NascarConfigEntry, series_id: int, key: str) -> None:
        super().__init__(entry.runtime_data.scoring)
        self.series_id = series_id
        self.key = key
        self.kind: ScoringKind = "stages" if key == "scored_stages" else "points"
        self._attr_unique_id = f"{entry.entry_id}_{series_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = series_device(entry, series_id)

    @property
    def available(self) -> bool:
        return self.coordinator.feed(self.kind, self.series_id) is not None

    @property
    def native_value(self) -> int | None:
        feed = self.coordinator.feed(self.kind, self.series_id)
        if feed is None:
            return None
        if self.key == "scored_stages":
            # Published result sets, not inferred completed/official stages.
            return sum(bool(stage.results) for stage in feed.stages)
        leaders = [row for row in feed.points if row.position == 1]
        return leaders[0].driver_id if len(leaders) == 1 else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        feed = self.coordinator.feed(self.kind, self.series_id)
        if feed is None:
            return None
        context = feed.contexts[0]
        return {
            "series_id": context.series_id,
            "race_id": context.race_id,
            "run_id": context.run_id,
            "classification": feed.classification,
        }
