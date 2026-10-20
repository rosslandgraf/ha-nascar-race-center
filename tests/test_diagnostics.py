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
