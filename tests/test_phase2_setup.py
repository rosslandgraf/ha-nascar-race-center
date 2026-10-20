"""Real HA setup exercises CF transport, parsers, calendars and outages together."""

from collections import Counter

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nascar_race_center.const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_FAVORITE_DRIVERS,
    CONF_LIVE_INTERVAL,
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_CF,
)
from custom_components.nascar_race_center.endpoints import (
    BASE_URL,
    DRIVERS,
    LIVE_FEED,
    TRACKS,
    schedule_feed_path,
    schedule_path,
)


@pytest.mark.parametrize("failed_reference", ["drivers", "tracks"])
async def test_cf_setup_reuses_schedule_with_reference_outage_and_reload(
    hass: HomeAssistant, aioclient_mock, freezer, failed_reference: str
) -> None:
    """One optional outage cannot hide three series, calendars or stable IDs."""
    freezer.move_to("2026-10-20T12:00:00+00:00")
    basic: dict[str, list[dict[str, object]]] = {}
    for series_id in (1, 2, 3):
        race_id = 9900 + series_id
        basic[f"series_{series_id}"] = [
            {
                "race_id": race_id,
                "series_id": series_id,
                "race_name": f"Fictional Series {series_id} Weekend",
                "race_season": 2026,
                "date_scheduled": "2026-10-24T18:00:00Z",
                "track_id": 99001,
                "track_name": "Demonstration Speedway",
            }
        ]
        aioclient_mock.get(
            BASE_URL + schedule_feed_path(2026, series_id),
            json=[
                {
                    **basic[f"series_{series_id}"][0],
                    "event_name": name,
                    "run_type": kind,
                    "start_time_utc": start,
                    "end_time_utc": end,
                }
                for kind, name, start, end in (
                    (1, "Practice", "2026-10-22T18:00:00Z", "2026-10-22T19:00:00Z"),
                    (2, "Qualifying", "2026-10-23T18:00:00Z", "2026-10-23T19:00:00Z"),
                    (3, "Race", "2026-10-24T18:00:00Z", "2026-10-24T21:00:00Z"),
                )
            ],
        )
    aioclient_mock.get(BASE_URL + schedule_path(2026), json=basic)
    aioclient_mock.get(BASE_URL + LIVE_FEED, text="null")
    drivers = {
        "response": [
            {
                "Nascar_Driver_ID": 99001,
                "Full_Name": "Fictional Driver",
                "Driver_Series": "nascar-cup-series",
                "Badge": "07",
                "Team": "Demonstration Team",
            }
        ]
    }
    tracks = {
        "items": [
            {
                "track_id": 99001,
                "track_name": "Demonstration Speedway",
                "city": "Example City",
                "state": "Example State",
                "length": 1.5,
            }
        ]
    }
    for feed, path, payload in (
        ("drivers", DRIVERS, drivers),
        ("tracks", TRACKS, tracks),
    ):
        aioclient_mock.get(
            BASE_URL + path,
            status=503 if feed == failed_reference else 200,
            json=payload,
        )
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            CONF_PROVIDER: PROVIDER_CF,
            CONF_DATA_USE_AUTHORIZED: True,
            CONF_SERIES: ["1", "2", "3"],
            CONF_LIVE_INTERVAL: 300,
            CONF_FAVORITE_DRIVERS: ["99001"],
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.reference.data.failed_feeds == {failed_reference}
    assert entry.runtime_data.schedule.data.failed_series == frozenset()
    registry = er.async_get(hass)
    calendar_ids = []
    for series_id in (1, 2, 3):
        next_race = registry.async_get_entity_id(
            "sensor", DOMAIN, f"{entry.entry_id}_{series_id}_next_race"
        )
        assert (
            hass.states.get(next_race).state == f"Fictional Series {series_id} Weekend"
        )
        calendar_id = registry.async_get_entity_id(
            "calendar", DOMAIN, f"{entry.entry_id}_{series_id}_calendar"
        )
        assert calendar_id is not None
        calendar_ids.append(calendar_id)
        response = await hass.services.async_call(
            "calendar",
            "get_events",
            {
                "entity_id": calendar_id,
                "start_date_time": "2026-10-21T00:00:00Z",
                "end_date_time": "2026-10-26T00:00:00Z",
            },
            blocking=True,
            return_response=True,
        )
        events = response[calendar_id]["events"]
        assert len(events) == 4  # Three sessions and the derived weekend date marker.
        assert any("Practice" in event["summary"] for event in events)
        assert all("Demonstration Speedway" in event["description"] for event in events)
    calls = Counter(str(call[1]) for call in aioclient_mock.mock_calls)
    assert calls[BASE_URL + schedule_path(2026)] == 1
    assert aioclient_mock.call_count == 7
    # Calendar reads and all selected-series refreshes reuse the same HTTP cache.
    await entry.runtime_data.schedule.async_refresh()
    await entry.runtime_data.reference.async_refresh()
    await hass.async_block_till_done()
    assert aioclient_mock.call_count == 7
    before = {
        entity.unique_id: entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
    }
    old = entry.runtime_data
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.runtime_data is not old
    assert old.schedule._stopped and old.live._stopped
    assert {
        entity.unique_id: entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
    } == before
    # Changing favorites while an optional feed is down preserves calendars and
    # creates a missing-metadata selection without fabricating driver details.
    hass.config_entries.async_update_entry(
        entry, options={**entry.data, CONF_FAVORITE_DRIVERS: ["99001", "99002"]}
    )
    await hass.async_block_till_done()
    assert entry.runtime_data.favorites.ids == (99001, 99002)
    assert all(hass.states.get(entity_id) is not None for entity_id in calendar_ids)
    assert registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_driver_99002_metadata"
    )
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert not async_get_clientsession(hass).closed
