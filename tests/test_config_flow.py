"""Exercise user-facing onboarding and options using Home Assistant's flow manager."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nascar_race_center.const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_LIVE_INTERVAL,
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_CF,
    PROVIDER_DEMO,
)


def user_input(**overrides: object) -> dict[str, object]:
    """Build valid form data without requiring any NASCAR account."""
    return {
        CONF_PROVIDER: PROVIDER_DEMO,
        CONF_SERIES: ["1", "2", "3"],
        CONF_DATA_USE_AUTHORIZED: False,
        CONF_LIVE_INTERVAL: 300,
        **overrides,
    }


async def test_user_flow_defaults_to_offline_demo(hass: HomeAssistant) -> None:
    """The first installation can complete without network access or credentials."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    with patch(
        "custom_components.nascar_race_center.async_setup_entry",
        new=AsyncMock(return_value=True),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=user_input()
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_PROVIDER] == PROVIDER_DEMO
    assert result["data"][CONF_SERIES] == ["1", "2", "3"]
    assert result["result"].unique_id == DOMAIN


async def test_duplicate_instance_aborts(hass: HomeAssistant) -> None:
    """A single installation monitors multiple selected series."""
    entry = MockConfigEntry(domain=DOMAIN, data=user_input(), unique_id=DOMAIN)
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_cf_requires_explicit_authorization(hass: HomeAssistant) -> None:
    """Selecting CF cannot silently enable unapproved automated polling."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data=user_input(**{CONF_PROVIDER: PROVIDER_CF}),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][CONF_DATA_USE_AUTHORIZED] == "authorization_required"


@pytest.mark.parametrize("series", [[], ["4"], ["1", "invalid"], "1", 1, None])
async def test_reject_empty_or_unknown_series(
    hass: HomeAssistant, series: object
) -> None:
    """Do not create unusable entries or route requests to unknown series."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data=user_input(**{CONF_SERIES: series}),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][CONF_SERIES] == "invalid_series"


async def test_options_preserve_authorization_gate(hass: HomeAssistant) -> None:
    """The options flow enforces the same data-use gate as onboarding."""
    entry = MockConfigEntry(domain=DOMAIN, data=user_input(), unique_id=DOMAIN)
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input(**{CONF_PROVIDER: PROVIDER_CF})
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][CONF_DATA_USE_AUTHORIZED] == "authorization_required"


async def test_options_update_selected_series(hass: HomeAssistant) -> None:
    """Users can select the monitored series entirely in the UI."""
    entry = MockConfigEntry(domain=DOMAIN, data=user_input(), unique_id=DOMAIN)
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input(**{CONF_SERIES: ["3"]})
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_SERIES] == ["3"]


@pytest.mark.parametrize("provider", ["unrecognized", "", None])
async def test_reject_unknown_provider(hass: HomeAssistant, provider: object) -> None:
    """Direct flow submissions cannot bypass the supported provider choices."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data=user_input(**{CONF_PROVIDER: provider}),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][CONF_PROVIDER] == "invalid_provider"


@pytest.mark.parametrize("interval", [0, 59, 299, 3601, "300", "invalid", True])
async def test_reject_polling_outside_safe_bounds(
    hass: HomeAssistant, interval: object
) -> None:
    """Malformed requests cannot enable rapid polling through the flow manager."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data=user_input(**{CONF_LIVE_INTERVAL: interval}),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][CONF_LIVE_INTERVAL] == "invalid_interval"


@pytest.mark.parametrize("authorization", ["false", "true", 1])
async def test_cf_authorization_must_be_boolean_true(
    hass: HomeAssistant, authorization: object
) -> None:
    """Truthy strings/numbers must not substitute for explicit user consent."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data=user_input(
            **{
                CONF_PROVIDER: PROVIDER_CF,
                CONF_DATA_USE_AUTHORIZED: authorization,
            }
        ),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"][CONF_DATA_USE_AUTHORIZED] == "authorization_required"


@pytest.mark.parametrize(
    "overrides",
    [
        {"racing_events": "yes"},
        {"event_types": ["official_results"]},
        {"favorite_event_types": ["stage_finish"]},
        {"event_types": ["favorite_lead"]},
        {"favorite_event_types": ["lead_changed"]},
        {"event_types": None},
        {"event_top_n": 0},
        {"event_top_n": 41},
        {"event_top_n": True},
        {"event_top_n": 3.5},
        {"reminder_minutes": 0},
        {"reminder_minutes": 1441},
        {"reminder_minutes": False},
    ],
)
async def test_event_option_validation(hass, overrides):
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data=user_input(**overrides),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_events"}


async def test_events_can_be_selected_then_cleared_without_changing_existing_ids(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data=user_input(
            racing_events=True,
            event_types=["flag_changed"],
            favorite_event_types=["favorite_lead"],
        ),
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=user_input(
            racing_events=True, event_top_n=5.0, reminder_minutes=15.0
        ),
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["event_types"] == []
    assert entry.options["favorite_event_types"] == []
    assert type(entry.options["event_top_n"]) is int
    assert entry.options["reminder_minutes"] == 15
    assert entry.unique_id == DOMAIN
