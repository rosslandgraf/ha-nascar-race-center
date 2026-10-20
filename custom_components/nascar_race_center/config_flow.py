"""UI configuration for NASCAR Race Center."""

from typing import Any

import probatio
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_LIVE_INTERVAL,
    CONF_PROVIDER,
    CONF_SERIES,
    DEFAULT_LIVE_INTERVAL,
    DEFAULT_SERIES,
    DOMAIN,
    MAX_LIVE_INTERVAL,
    MIN_LIVE_INTERVAL,
    NAME,
    PROVIDER_CF,
    PROVIDER_DEMO,
    SERIES_NAMES,
)


def _schema(values: dict[str, Any]) -> probatio.Schema:
    """Provide the same validated controls for onboarding and options."""
    provider_options: list[selector.SelectOptionDict] = [
        {"value": PROVIDER_DEMO, "label": "Offline demonstration"},
        {"value": PROVIDER_CF, "label": "NASCAR CF (requires data-use permission)"},
    ]
    series_options: list[selector.SelectOptionDict] = [
        {"value": str(key), "label": name} for key, name in SERIES_NAMES.items()
    ]
    return probatio.Schema(
        {
            probatio.Required(
                CONF_PROVIDER, default=values.get(CONF_PROVIDER, PROVIDER_DEMO)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=provider_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            probatio.Required(
                CONF_SERIES, default=values.get(CONF_SERIES, DEFAULT_SERIES)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=series_options,
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            probatio.Required(
                CONF_DATA_USE_AUTHORIZED,
                default=values.get(CONF_DATA_USE_AUTHORIZED, False),
            ): selector.BooleanSelector(),
            probatio.Required(
                CONF_LIVE_INTERVAL,
                default=values.get(CONF_LIVE_INTERVAL, DEFAULT_LIVE_INTERVAL),
            ): probatio.All(
                probatio.Coerce(int),
                probatio.Range(min=MIN_LIVE_INTERVAL, max=MAX_LIVE_INTERVAL),
            ),
        }
    )


def _validate(values: dict[str, Any]) -> dict[str, str]:
    """Validate semantic choices without contacting NASCAR during configuration."""
    if not isinstance(values.get(CONF_PROVIDER), str) or values[CONF_PROVIDER] not in {
        PROVIDER_DEMO,
        PROVIDER_CF,
    }:
        return {CONF_PROVIDER: "invalid_provider"}
    interval = values.get(CONF_LIVE_INTERVAL, DEFAULT_LIVE_INTERVAL)
    if (
        not isinstance(interval, int)
        or isinstance(interval, bool)
        or not MIN_LIVE_INTERVAL <= interval <= MAX_LIVE_INTERVAL
    ):
        return {CONF_LIVE_INTERVAL: "invalid_interval"}
    if (
        not isinstance(values.get(CONF_SERIES), list)
        or not values[CONF_SERIES]
        or any(
            not isinstance(value, str) or value not in {"1", "2", "3"}
            for value in values[CONF_SERIES]
        )
    ):
        return {CONF_SERIES: "invalid_series"}
    if (
        values[CONF_PROVIDER] == PROVIDER_CF
        and values.get(CONF_DATA_USE_AUTHORIZED) is not True
    ):
        return {CONF_DATA_USE_AUTHORIZED: "authorization_required"}
    return {}


class NascarRaceCenterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create the single configurable NASCAR Race Center instance."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure offline demonstration or explicitly authorized CF access."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        errors = _validate(user_input) if user_input is not None else {}
        if user_input is not None and not errors:
            return self.async_create_entry(title=NAME, data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=_schema(user_input or {}), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Offer the same choices after installation."""
        return NascarRaceCenterOptionsFlow()


class NascarRaceCenterOptionsFlow(OptionsFlow):
    """Update choices and reload through the config entry listener."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the configured provider and selected series."""
        errors = _validate(user_input) if user_input is not None else {}
        if user_input is not None and not errors:
            return self.async_create_entry(title="", data=user_input)
        values = {
            **self.config_entry.data,
            **self.config_entry.options,
            **(user_input or {}),
        }
        return self.async_show_form(
            step_id="init", data_schema=_schema(values), errors=errors
        )
