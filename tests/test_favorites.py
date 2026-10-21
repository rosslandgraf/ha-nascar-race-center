"""Favorite identity, searchable UI and real HA metadata entity regressions."""

from dataclasses import replace
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nascar_race_center.const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_FAVORITE_DRIVERS,
    CONF_LIVE_INTERVAL,
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_CF,
    PROVIDER_DEMO,
)
from custom_components.nascar_race_center.favorites import FavoriteDriverRegistry
from custom_components.nascar_race_center.reference import Driver, DriverAssociation


def form_values(**overrides: object) -> dict[str, object]:
    """Phase 1 settings stay valid with an optional stable-ID selection."""
    return {
        CONF_PROVIDER: PROVIDER_DEMO,
        CONF_SERIES: ["1", "2", "3"],
        CONF_DATA_USE_AUTHORIZED: False,
        CONF_LIVE_INTERVAL: 300,
        **overrides,
    }


def test_registry_identity_survives_number_team_name_and_series_changes() -> None:
    """Reference changes update metadata without changing selected NASCAR IDs."""
    favorites = FavoriteDriverRegistry(["123", "00456", "123"])
    before = Driver(123, "Synthetic driver", series_ids=(1,), car_number="04", team="A")
    after = Driver(123, "Updated driver", series_ids=(2, 3), car_number="9", team="B")
    assert favorites.ids == (123, 456)
    assert favorites.get(123, {123: before}) == before
    assert favorites.get(123, {123: after}) == after
    assert favorites.get(456, {123: after}) is None
    assert favorites.contains(456)
    assert favorites.selected({123: after, 999: Driver(999, "Unselected")}) == (after,)


async def test_favorites_config_normalizes_ids_and_requires_no_directory(
    hass: HomeAssistant,
) -> None:
    """An unavailable CF directory cannot prevent stable-ID onboarding."""
    with patch(
        "custom_components.nascar_race_center.async_setup_entry",
        new=AsyncMock(return_value=True),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data=form_values(
                **{
                    CONF_PROVIDER: PROVIDER_CF,
                    CONF_DATA_USE_AUTHORIZED: True,
                    CONF_FAVORITE_DRIVERS: ["00321", "123", "321"],
                }
            ),
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_FAVORITE_DRIVERS] == ["123", "321"]


async def test_onboarding_favorites_wait_for_a_source_specific_directory(
    hass: HomeAssistant,
) -> None:
    """Switching the source selector cannot present demo names as CF drivers."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    driver_selector = next(
        value
        for key, value in result["data_schema"].schema.items()
        if key.schema == CONF_FAVORITE_DRIVERS
    )
    assert driver_selector.config["options"] == []
    assert driver_selector.config["custom_value"] is True
    validated = result["data_schema"](
        form_values(**{CONF_FAVORITE_DRIVERS: ["123", "456"]})
    )
    assert validated[CONF_FAVORITE_DRIVERS] == ["123", "456"]


async def test_source_switch_keeps_ids_without_demo_names_in_cf_options(
    hass: HomeAssistant,
) -> None:
    """Changing sources never remaps IDs by name or reuses a demo directory."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=form_values(**{CONF_FAVORITE_DRIVERS: ["99001"]}),
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    driver_selector = next(
        value
        for key, value in result["data_schema"].schema.items()
        if key.schema == CONF_FAVORITE_DRIVERS
    )
    assert any(
        item["label"].startswith("Demo: ") for item in driver_selector.config["options"]
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=form_values(
            **{
                CONF_PROVIDER: PROVIDER_CF,
                CONF_DATA_USE_AUTHORIZED: True,
                CONF_FAVORITE_DRIVERS: ["99001"],
            }
        ),
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_FAVORITE_DRIVERS] == ["99001"]
    result = await hass.config_entries.options.async_init(entry.entry_id)
    driver_selector = next(
        value
        for key, value in result["data_schema"].schema.items()
        if key.schema == CONF_FAVORITE_DRIVERS
    )
    assert driver_selector.config["options"] == [
        {"value": "99001", "label": "NASCAR driver ID 99001 (metadata unavailable)"}
    ]


@pytest.mark.parametrize(
    "favorites",
    [
        None,
        "123",
        [123],
        ["0"],
        ["-1"],
        ["Driver name"],
        ["١٢٣"],
        ["1" * 21],
        [str(value) for value in range(1, 52)],
    ],
)
async def test_favorite_config_rejects_names_numbers_and_unbounded_selections(
    hass: HomeAssistant, favorites: object
) -> None:
    """Only explicitly entered positive NASCAR IDs fit the persisted contract."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data=form_values(**{CONF_FAVORITE_DRIVERS: favorites}),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][CONF_FAVORITE_DRIVERS] == "invalid_favorite_drivers"


async def test_unavailable_directory_options_preserve_favorites_and_series_changes(
    hass: HomeAssistant,
) -> None:
    """Cached or manually entered favorites remain editable during an outage."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=form_values(
            **{
                CONF_PROVIDER: PROVIDER_CF,
                CONF_DATA_USE_AUTHORIZED: True,
                CONF_FAVORITE_DRIVERS: ["123", "456"],
            }
        ),
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    selector = next(
        value
        for key, value in result["data_schema"].schema.items()
        if key.schema == CONF_FAVORITE_DRIVERS
    )
    assert selector.config["multiple"] is True
    assert selector.config["custom_value"] is True
    assert selector.config["mode"] == "dropdown"
    assert {item["value"] for item in selector.config["options"]} == {"123", "456"}
    assert all(
        "metadata unavailable" in item["label"] for item in selector.config["options"]
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=form_values(
            **{
                CONF_PROVIDER: PROVIDER_CF,
                CONF_DATA_USE_AUTHORIZED: True,
                CONF_SERIES: ["3"],
                CONF_FAVORITE_DRIVERS: ["123", "456"],
            }
        ),
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_FAVORITE_DRIVERS] == ["123", "456"]


def favorite_entity_id(
    hass: HomeAssistant, entry: MockConfigEntry, driver_id: int
) -> str:
    """Resolve persisted identity independently of display names and car numbers."""
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_driver_{driver_id}_metadata"
    )
    assert entity_id is not None
    return entity_id


async def setup_favorites(
    hass: HomeAssistant, ids: list[str], drivers: tuple[Driver, ...]
) -> MockConfigEntry:
    """Use actual HA setup and entity platforms with only reference I/O mocked."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=form_values(**{CONF_FAVORITE_DRIVERS: ids}),
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.reference_provider.DemoReferenceProvider.async_get_drivers",
        new=AsyncMock(return_value=drivers),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_metadata_entities_keep_ids_across_reference_changes_and_outages(
    hass: HomeAssistant,
) -> None:
    """Multiple favorites get current metadata without fabricated live metrics."""
    entry = await setup_favorites(
        hass,
        ["123", "456", "999"],
        (
            Driver(123, "Synthetic A", series_ids=(1,), car_number="04", team="A"),
            Driver(
                456,
                "Synthetic B",
                series_ids=(2, 3),
                associations=(
                    DriverAssociation(series_id=2, car_number="07"),
                    DriverAssociation(series_id=3, car_number="17"),
                ),
            ),
        ),
    )
    entity_id = favorite_entity_id(hass, entry, 123)
    state = hass.states.get(entity_id)
    assert state.state == "Synthetic A"
    assert state.attributes["car_number"] == "04"
    assert "position" not in state.attributes
    multiseries = hass.states.get(favorite_entity_id(hass, entry, 456))
    assert multiseries.attributes["car_number"] is None
    assert [
        (item["series_id"], item["car_number"])
        for item in multiseries.attributes["series_metadata"]
    ] == [(2, "07"), (3, "17")]
    assert (
        hass.states.get(favorite_entity_id(hass, entry, 999)).state == STATE_UNAVAILABLE
    )
    coordinator = entry.runtime_data.reference
    changed = Driver(123, "Renamed A", series_ids=(2, 3), car_number="9", team="B")
    coordinator.async_set_updated_data(
        replace(
            coordinator.data, drivers={123: changed, 456: Driver(456, "Synthetic B")}
        )
    )
    await hass.async_block_till_done()
    assert favorite_entity_id(hass, entry, 123) == entity_id
    state = hass.states.get(entity_id)
    assert state.state == "Renamed A"
    assert state.attributes["series_ids"] == [2, 3]
    assert state.attributes["team"] == "B"
    coordinator.async_set_updated_data(
        replace(coordinator.data, failed_feeds=frozenset({"drivers"}))
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE
    assert entry.runtime_data.favorites.ids == (123, 456, 999)
    coordinator.async_set_updated_data(
        replace(
            coordinator.data,
            failed_feeds=frozenset(),
            updated_at={
                key: value - timedelta(days=8)
                for key, value in coordinator.data.updated_at.items()
            },
        )
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize("omitted", [False, True])
@pytest.mark.parametrize("stored_in_options", [False, True])
async def test_options_clear_all_favorites_persists_and_preserves_other_entities(
    hass: HomeAssistant, omitted: bool, stored_in_options: bool
) -> None:
    """An empty UI selection overrides saved data and removes only favorites."""
    entry = await setup_favorites(
        hass,
        ["99001", "99002"],
        (Driver(99001, "Synthetic A"), Driver(99002, "Synthetic B")),
    )
    if stored_in_options:
        hass.config_entries.async_update_entry(
            entry, options={CONF_FAVORITE_DRIVERS: ["99001", "99002"]}
        )
        await hass.async_block_till_done()
    registry = er.async_get(hass)
    devices = dr.async_get(hass)
    removed = [
        entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
        if entity.platform == DOMAIN
        and entity.unique_id.startswith(f"{entry.entry_id}_driver_")
    ]
    removed_devices = [registry.async_get(value).device_id for value in removed]
    unrelated = registry.async_get_or_create(
        "sensor", "other_integration", "unrelated", config_entry=entry
    )
    hass.states.async_set(unrelated.entity_id, "unchanged")
    retained = {
        entity.unique_id: (entity.entity_id, entity.device_id)
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
        if entity.entity_id not in removed
    }
    enabled = {
        entity_id for entity_id, _ in retained.values() if hass.states.get(entity_id)
    }
    result = await hass.config_entries.options.async_init(entry.entry_id)
    submitted = form_values()
    marker = next(
        key
        for key in result["data_schema"].schema
        if key.schema == CONF_FAVORITE_DRIVERS
    )
    assert marker.description["suggested_value"] == ["99001", "99002"]
    if not omitted:
        submitted[CONF_FAVORITE_DRIVERS] = []
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=submitted
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_FAVORITE_DRIVERS] == []
    assert entry.runtime_data.favorites.ids == ()
    for entity_id, device_id in zip(removed, removed_devices, strict=True):
        assert registry.async_get(entity_id) is None
        assert hass.states.get(entity_id) is None
        assert device_id is not None
        assert devices.async_get(device_id) is None
    assert {
        entity.unique_id: (entity.entity_id, entity.device_id)
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
    } == retained
    assert hass.states.get(unrelated.entity_id).state == "unchanged"
    for entity_id in enabled:
        assert hass.states.get(entity_id) is not None
    for _, device_id in retained.values():
        if device_id is not None:
            assert devices.async_get(device_id) is not None
    # Reopening the UI and reloading must not revive favorites from entry.data.
    form = await hass.config_entries.options.async_init(entry.entry_id)
    marker = next(
        key for key in form["data_schema"].schema if key.schema == CONF_FAVORITE_DRIVERS
    )
    assert marker.description["suggested_value"] == []
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.options[CONF_FAVORITE_DRIVERS] == []
    assert entry.runtime_data.favorites.ids == ()
    assert all(registry.async_get(value) is None for value in removed)
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_favorites_options_remove_add_and_reload_without_duplicates(
    hass: HomeAssistant,
) -> None:
    """Removed selections lose only their own entity; retained IDs survive reload."""
    drivers = (
        Driver(123, "Synthetic A", series_ids=(1,)),
        Driver(456, "Synthetic B", series_ids=(3,)),
    )
    entry = await setup_favorites(hass, ["123", "456"], drivers)
    retained = favorite_entity_id(hass, entry, 123)
    removed = favorite_entity_id(hass, entry, 456)
    retained_device = er.async_get(hass).async_get(retained).device_id
    removed_device = er.async_get(hass).async_get(removed).device_id
    assert retained_device is not None
    assert removed_device is not None
    previous_reference = entry.runtime_data.reference
    result = await hass.config_entries.options.async_init(entry.entry_id)
    driver_selector = next(
        value
        for key, value in result["data_schema"].schema.items()
        if key.schema == CONF_FAVORITE_DRIVERS
    )
    assert any(
        "Synthetic A" in item["label"] for item in driver_selector.config["options"]
    )
    with patch(
        "custom_components.nascar_race_center.reference_provider.DemoReferenceProvider.async_get_drivers",
        new=AsyncMock(return_value=drivers),
    ):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input=form_values(
                **{CONF_SERIES: ["3"], CONF_FAVORITE_DRIVERS: ["123", "789"]}
            ),
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert favorite_entity_id(hass, entry, 123) == retained
    assert er.async_get(hass).async_get(retained).device_id == retained_device
    assert dr.async_get(hass).async_get(retained_device) is not None
    assert er.async_get(hass).async_get(removed) is None
    assert dr.async_get(hass).async_get(removed_device) is None
    assert hass.states.get(removed) is None
    assert (
        hass.states.get(favorite_entity_id(hass, entry, 789)).state == STATE_UNAVAILABLE
    )
    assert entry.runtime_data.favorites.ids == (123, 789)
    assert entry.runtime_data.reference is not previous_reference
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_clearing_favorite_keeps_device_used_by_another_entity(
    hass: HomeAssistant,
) -> None:
    """Favorite cleanup never deletes a device that still has another entity."""
    entry = await setup_favorites(hass, ["99001"], (Driver(99001, "Synthetic"),))
    registry = er.async_get(hass)
    favorite = favorite_entity_id(hass, entry, 99001)
    device_id = registry.async_get(favorite).device_id
    assert device_id is not None
    other = registry.async_get_or_create(
        "sensor",
        "other_integration",
        "shared_device",
        config_entry=entry,
        device_id=device_id,
    )
    hass.states.async_set(other.entity_id, "unchanged")
    form = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(
        form["flow_id"], user_input=form_values(**{CONF_FAVORITE_DRIVERS: []})
    )
    await hass.async_block_till_done()
    assert registry.async_get(favorite) is None
    assert registry.async_get(other.entity_id).device_id == device_id
    assert hass.states.get(other.entity_id).state == "unchanged"
    assert dr.async_get(hass).async_get(device_id) is not None
    assert await hass.config_entries.async_unload(entry.entry_id)
