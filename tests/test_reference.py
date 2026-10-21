"""Tiny synthetic reference contracts, without captured NASCAR datasets."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from custom_components.nascar_race_center.models import SchemaError
from custom_components.nascar_race_center.reference import (
    MAX_DRIVER_ROWS,
    MAX_TRACK_ROWS,
    Driver,
    Track,
    parse_drivers,
    parse_tracks,
)
from custom_components.nascar_race_center.reference_provider import (
    CFReferenceProvider,
    DemoReferenceProvider,
)

FIXTURES = Path(__file__).parent / "fixtures" / "nascar"


def test_driver_identity_groups_multiple_series_without_a_roster_claim() -> None:
    """Separate series entries share identity and preserve distinct metadata."""
    drivers = parse_drivers(json.loads((FIXTURES / "drivers.json").read_text()))
    driver = drivers[0]
    assert driver.driver_id == 99011
    assert driver.series_ids == (1, 2)
    assert driver.car_number is None
    assert driver.team is None
    assert driver.association_for(1).car_number == "07"
    assert driver.association_for(2).team == "Example Second Team"
    assert driver.association_for(3) is None
    assert drivers[1].series_ids == (3,)
    assert drivers[1].car_number == "03"
    assert drivers[2].series_ids == ()


def test_driver_changes_number_team_series_and_name_keep_id() -> None:
    """Mutable display facts never replace the NASCAR driver identity."""
    row = {
        "Nascar_Driver_ID": 99011,
        "Full_Name": "Example Driver",
        "Driver_Series": "nascar-cup-series",
        "Badge": "07",
        "Team": "Previous Team",
    }
    before = parse_drivers({"response": [row]})[0]
    row.update(
        Full_Name="Example Updated Driver",
        Driver_Series="nascar-craftsman-truck-series",
        Badge="99",
        Team="New Team",
    )
    after = parse_drivers({"response": [row]})[0]
    assert before.driver_id == after.driver_id
    assert (before.series_ids, after.series_ids) == ((1,), (3,))
    assert (before.car_number, after.car_number) == ("07", "99")
    assert (before.team, after.team) == ("Previous Team", "New Team")


def test_unknown_series_and_optional_fields_are_not_invented() -> None:
    """Unknown associations and logo URLs cannot become named manufacturer facts."""
    driver = parse_drivers(
        {
            "response": [
                {
                    "Nascar_Driver_ID": "99011",
                    "Full_Name": " Example Driver ",
                    "Driver_Series": "unverified-series-format",
                    "Badge": "https://example.invalid/badge.png",
                    "Manufacturer": "https://example.invalid/brand.png",
                    "Rookie_Year_Series_3": 2020,
                    "Points": "1000",
                    "Image": "https://example.invalid/image.png",
                }
            ]
        }
    )[0]
    assert driver.name == "Example Driver"
    assert driver.series_ids == ()
    assert driver.series_label == "unverified-series-format"
    assert driver.car_number is None
    assert driver.team is None
    assert driver.manufacturer is None
    assert not hasattr(driver, "points")
    assert not hasattr(driver, "image")


def test_invalid_directory_rows_do_not_create_unstable_driver_ids() -> None:
    """Secondary IDs/names/car numbers never supply an identity fallback."""
    payload = {
        "response": [
            None,
            {"Driver_ID": 88, "Full_Name": "Unstable", "Badge": "9"},
            {"Nascar_Driver_ID": True, "Full_Name": "Boolean"},
            {"Nascar_Driver_ID": "9" * 5000, "Full_Name": "Oversized ID"},
            {"Nascar_Driver_ID": 99011, "Full_Name": "Valid Driver"},
        ]
    }
    drivers = parse_drivers(payload)
    assert [(driver.driver_id, driver.name) for driver in drivers] == [
        (99011, "Valid Driver")
    ]
    assert drivers[0].series_ids == ()


@pytest.mark.parametrize(
    "payload", [None, [], {}, {"response": {}}, {"response": [None]}]
)
def test_bad_driver_envelopes_are_not_empty_directories(payload: object) -> None:
    with pytest.raises(SchemaError):
        parse_drivers(payload)


def test_duplicate_driver_rows_and_conflicting_identity() -> None:
    row = {"Nascar_Driver_ID": 99011, "Full_Name": "Example", "Badge": "00"}
    assert parse_drivers({"response": [row, row]})[0].car_number == "00"
    with pytest.raises(SchemaError):
        parse_drivers({"response": [row, {**row, "Full_Name": "Other Person"}]})


def test_ambiguous_same_series_metadata_is_preserved_without_guessing() -> None:
    row = {
        "Nascar_Driver_ID": 99011,
        "Full_Name": "Example",
        "Driver_Series": "nascar-cup-series",
        "Badge": "07",
    }
    driver = parse_drivers({"response": [row, {**row, "Badge": "17"}]})[0]
    assert len(driver.associations) == 2
    assert driver.car_number is None
    assert driver.association_for(1) is None


def test_track_facts_and_missing_values() -> None:
    tracks = parse_tracks(json.loads((FIXTURES / "tracks.json").read_text()))
    assert tracks[0] == Track(
        99001,
        "Example Speedway",
        "Example City",
        "Example State",
        1.5,
        "Intermediate",
        "Asphalt",
    )
    assert tracks[0].location == "Example City, Example State"
    assert tracks[1].location is None
    assert tracks[1].length_miles is None
    assert not hasattr(tracks[0], "timezone")


@pytest.mark.parametrize(
    "length", [None, "", "bad", True, 0, -1, "NaN", "inf", float("inf")]
)
def test_invalid_lengths_remain_unknown(length: object) -> None:
    track = parse_tracks(
        {"items": [{"track_id": 99001, "track_name": "Example", "length": length}]}
    )[0]
    assert track.length_miles is None


@pytest.mark.parametrize("payload", [None, [], {}, {"items": {}}, {"items": [None]}])
def test_bad_track_envelopes_are_not_empty_directories(payload: object) -> None:
    with pytest.raises(SchemaError):
        parse_tracks(payload)


def test_duplicate_track_conflicts_and_record_limits() -> None:
    row = {"track_id": 99001, "track_name": "Example"}
    assert len(parse_tracks({"items": [row, row]})) == 1
    with pytest.raises(SchemaError):
        parse_tracks({"items": [row, {**row, "track_name": "Conflict"}]})
    with pytest.raises(SchemaError):
        parse_tracks({"items": [row] * (MAX_TRACK_ROWS + 1)})
    with pytest.raises(SchemaError):
        parse_drivers({"response": [None] * (MAX_DRIVER_ROWS + 1)})


def test_oversized_track_identity_does_not_break_other_venues() -> None:
    tracks = parse_tracks(
        {
            "items": [
                {"track_id": "9" * 5000, "track_name": "Unusable Identity"},
                {"track_id": 99001, "track_name": "Example Speedway"},
            ]
        }
    )
    assert [(track.track_id, track.name) for track in tracks] == [
        (99001, "Example Speedway")
    ]


def test_explicit_empty_reference_and_immutable_metadata() -> None:
    assert parse_drivers({"response": []}) == ()
    assert parse_tracks({"items": []}) == ()
    driver = Driver(99011, "Example")
    with pytest.raises(FrozenInstanceError):
        driver.name = "Changed"


async def test_reference_provider_reuses_shared_transport_and_daily_ttl() -> None:
    api = AsyncMock()
    api.async_get_json.side_effect = [{"response": []}, {"items": []}]
    provider = CFReferenceProvider(api)
    assert provider.api is api
    assert await provider.async_get_drivers() == ()
    assert await provider.async_get_tracks() == ()
    assert api.async_get_json.call_args_list[0].args == ("/cacher/drivers.json",)
    assert api.async_get_json.call_args_list[1].args == ("/cacher/tracks.json",)
    assert all(
        call.kwargs == {"minimum_ttl": 86400}
        for call in api.async_get_json.call_args_list
    )


async def test_demo_reference_provider_covers_all_series_without_network() -> None:
    provider = DemoReferenceProvider()
    drivers = await provider.async_get_drivers()
    assert {sid for driver in drivers for sid in driver.series_ids} == {1, 2, 3}
    assert all(driver.name.startswith("Demo ") for driver in drivers)
    assert await provider.async_get_tracks() == (await provider.async_get_tracks())
