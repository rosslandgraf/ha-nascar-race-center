"""Reported 915-row characteristics recreated with synthetic data, not a capture."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers import entity_registry as er
from test_init import demo_entry

from custom_components.nascar_race_center.config_flow import (
    _available_drivers,
    _driver_options,
)
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nascar_race_center.reference import parse_drivers
from custom_components.nascar_race_center.reference_provider import CFReferenceProvider


def driver(
    identifier=100001, name="Synthetic Driver", series="nascar-cup-series", **changes
):
    return {
        "Nascar_Driver_ID": identifier,
        "Driver_ID": "secondary-identity",
        "Full_Name": name,
        "Driver_Series": series,
        "Badge": "07",
        "Team": "Synthetic Team",
        "Driver_Post_Status": "publish",
        **changes,
    }


def directory_915():
    # Reported aggregate sizes plus the four minimal name conflicts are evidence;
    # all other records are fictional and do not reproduce the owner's directory.
    rows = [driver(100000 + i, f"Synthetic Driver {i}") for i in range(768)]
    pairs = [
        (4372, "Justin Carrol", "Justin S Carroll"),
        (4234, "Chad Finchum", "Mike Senica"),
        (4316, "Cj McLaughlin", "CJ McLaughlin"),
        (4151, "Tim Viens", "Timothy Viens"),
    ]
    rows.extend(driver(key, first) for key, first, _ in pairs)
    rows.extend(driver(key, second) for key, _, second in pairs)
    rows.extend(dict(rows[i % 768]) for i in range(123))
    rows.extend(driver(0, "Unidentified") for _ in range(16))
    assert len(rows) == 915
    return {"response": rows}


def test_915_rows_isolate_three_ambiguous_ids_and_merge_only_cosmetic_variants():
    report = {}
    result = parse_drivers(directory_915(), diagnostics=report)
    assert len(result) == 769
    assert report["source_rows"] == 915
    assert report["candidate_driver_ids"] == 772
    assert report["invalid_id_rows"] == 16
    assert report["ambiguous_driver_id_count"] == 3
    assert report["ambiguous_driver_ids_sample"] == [4151, 4234, 4372]
    assert next(d for d in result if d.driver_id == 4316).name == "CJ McLaughlin"
    assert len(report["usable_driver_ids_sample"]) == 20
    assert "Chad Finchum" not in repr(report)
    assert result == parse_drivers(
        {"response": list(reversed(directory_915()["response"]))}
    )


@pytest.mark.parametrize(
    "slug", ["nascar-oreilly-auto-parts-series", "nascar-xfinity-series"]
)
def test_current_and_historical_series_two_share_the_nascar_identity(slug):
    rows = [
        driver(series=slug),
        driver(series="nascar-cup-series", Badge="17"),
        driver(series="nascar-craftsman-truck-series", Badge="03"),
    ]
    result = parse_drivers({"response": rows})[0]
    assert result.driver_id == 100001
    assert result.series_ids == (1, 2, 3)
    assert result.association_for(2).car_number == "07"
    assert result.association_for(3).car_number == "03"
    assert result.car_number is None


@pytest.mark.parametrize("reverse", [False, True])
def test_draft_and_incomplete_rows_do_not_erase_better_published_associations(reverse):
    rows = [
        driver(),
        driver(Badge="", Team="0", Manufacturer="", Driver_Post_Status="draft"),
        driver(Team="", Manufacturer="Synthetic Make"),
    ]
    if reverse:
        rows.reverse()
    result = parse_drivers({"response": rows})[0]
    assert len(result.associations) == 1
    assert result.association_for(1).car_number == "07"
    assert result.association_for(1).team == "Synthetic Team"
    assert result.association_for(1).manufacturer == "Synthetic Make"
    assert result == parse_drivers({"response": list(reversed(rows))})[0]


def test_conflicting_metadata_and_unknown_associations_are_not_guessed():
    rows = [
        driver(),
        driver(Badge="09"),
        driver(
            100002,
            "Unknown association",
            series="unverified-slug",
            Team="1234",
            Manufacturer="https://example.invalid/logo",
            DOB="0001-01-01T00:00:00",
        ),
    ]
    result = parse_drivers({"response": rows})
    assert result[0].association_for(1) is None
    assert len(result[0].associations) == 2
    assert result[1].series_ids == ()
    assert result[1].team is None and result[1].manufacturer is None
    assert result[1].associations[0].team_raw == "1234"
    assert not hasattr(result[1], "dob")


async def test_reference_and_favorites_survive_quarantine_and_reload(
    hass,
):
    api = AsyncMock()
    payload = {
        "response": [
            driver(
                100001, "Synthetic Selected", series="nascar-oreilly-auto-parts-series"
            ),
            driver(4234, "Chad Finchum"),
            driver(4234, "Mike Senica"),
        ]
    }
    api.async_get_json.return_value = payload
    reference = CFReferenceProvider(api)
    entry = demo_entry(["1", "2", "3"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        entry, options={"favorite_drivers": ["100001", "4234"]}
    )
    # Exercise the normal integration/favorite entities; only provider I/O is mocked.
    with patch(
        "custom_components.nascar_race_center.DemoReferenceProvider",
        return_value=reference,
    ):
        reference.async_get_tracks = AsyncMock(return_value=())
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert set(entry.runtime_data.reference.data.drivers) == {100001}
        assert "drivers" not in entry.runtime_data.reference.data.failed_feeds
        assert entry.runtime_data.favorites.ids == (4234, 100001)
        choices = _driver_options(
            {"favorite_drivers": ["100001", "4234"]},
            tuple(entry.runtime_data.reference.data.drivers.values()),
        )
        assert "Synthetic Selected" in repr(choices)
        assert "O'Reilly" in repr(choices)
        before = {
            e.unique_id: e.entity_id
            for e in er.async_entries_for_config_entry(
                er.async_get(hass), entry.entry_id
            )
        }
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        after = {
            e.unique_id: e.entity_id
            for e in er.async_entries_for_config_entry(
                er.async_get(hass), entry.entry_id
            )
        }
        assert before == after
        assert entry.runtime_data.favorites.ids == (4234, 100001)
        diagnostics = await async_get_config_entry_diagnostics(hass, entry)
        assert diagnostics["reference"]["driver_normalization"][
            "ambiguous_driver_ids_sample"
        ] == [4234]
        assert diagnostics["reference"]["driver_count"] == 1
        assert diagnostics["packaging"]["resource_url"] == "/nascar_race_center/card.js"


async def test_rejected_reference_cannot_supply_cached_selector_names(hass):
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    runtime = entry.runtime_data
    assert _available_drivers(entry, "demo")
    from dataclasses import replace

    runtime.reference.async_set_updated_data(
        replace(runtime.reference.data, failed_feeds=frozenset({"drivers"}))
    )
    assert not _available_drivers(entry, "demo")
    choices = _driver_options(
        {"favorite_drivers": ["99001"]}, _available_drivers(entry, "demo")
    )
    assert choices == [
        {"value": "99001", "label": "NASCAR driver ID 99001 (metadata unavailable)"}
    ]
    assert (
        runtime.favorites.ids == ()
    )  # Opening the selector never mutates stored options.
