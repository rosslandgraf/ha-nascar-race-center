"""Ensure diagnostics report bounded health and exclude entry secrets/raw feed data."""

import json
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nascar_race_center.const import (
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_DEMO,
)
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nascar_race_center.models import LiveSnapshot


async def test_diagnostics_use_normalized_health_not_entry_payloads(
    hass: HomeAssistant,
) -> None:
    """Export only supported fields, never arbitrary config contents or raw bodies."""
    marker = "a-secret-that-must-not-appear-in-diagnostics"
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=())
    provider.async_get_live = AsyncMock(return_value=LiveSnapshot(2, 234, lap=15))
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PROVIDER: PROVIDER_DEMO,
            CONF_SERIES: ["2"],
            "token": marker,
            "Authorization": marker,
        },
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["provider"] == PROVIDER_DEMO
    assert diagnostics["selected_series"] == [2]
    assert diagnostics["schedule"]["race_counts"] == {"2": 0}
    assert diagnostics["live"]["series_id"] == 2
    assert diagnostics["live"]["race_id"] == 234
    assert diagnostics["live"]["field_availability"] == {
        "status": False,
        "flag": False,
        "lap": True,
        "source_updated_at": False,
    }
    assert marker not in json.dumps(diagnostics)
    assert "Authorization" not in diagnostics
    assert "raw" not in diagnostics


async def test_unknown_schedule_times_are_reported_without_guessing(
    hass: HomeAssistant,
) -> None:
    """A mixed schedule exposes its timing gaps and selects only an aware date."""
    from datetime import timedelta

    from homeassistant.helpers import entity_registry as er
    from homeassistant.util import dt as dt_util

    from custom_components.nascar_race_center.models import parse_schedule

    known = dt_util.utcnow() + timedelta(days=1)
    rows = [
        {
            "race_id": 1,
            "series_id": 1,
            "race_name": "Naive",
            "date_scheduled": "2026-11-01T12:30:00",
        },
        {
            "race_id": 2,
            "series_id": 1,
            "race_name": "Date only",
            "date_scheduled": "2026-11-01",
        },
        {
            "race_id": 3,
            "series_id": 1,
            "race_name": "Aware",
            "date_scheduled": known.isoformat(),
        },
    ]
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        return_value=parse_schedule({"series_1": rows}, 1)
    )
    provider.async_get_live = AsyncMock(return_value=None)
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: ["1"]}
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["schedule"]["unknown_start_time_counts"] == {"1": 2}
    assert diagnostics["schedule"]["timestamp_policy"] == "explicit_offset_required"
    registry = er.async_get(hass)
    count_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_1_scheduled_races"
    )
    count = hass.states.get(count_id)
    assert count.state == "3"
    assert count.attributes["unknown_start_times"] == 2
    assert entry.runtime_data.schedule.next_race(1).name == "Aware"
