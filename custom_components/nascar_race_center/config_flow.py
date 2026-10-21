"""UI configuration for NASCAR Race Center."""

from typing import TYPE_CHECKING, Any, cast

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
    CONF_FAVORITE_DRIVERS,
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
from .favorites import normalize_favorite_driver_ids
from .reference import Driver, demo_drivers

if TYPE_CHECKING:
    from . import NascarConfigEntry


def _available_drivers(
    entry: ConfigEntry | None, provider: object
) -> tuple[Driver, ...]:
    """Use cached reference metadata; opening a form never polls NASCAR."""
    if entry is not None:
        previous_provider = entry.options.get(
            CONF_PROVIDER, entry.data.get(CONF_PROVIDER, PROVIDER_DEMO)
        )
        if previous_provider == provider and getattr(entry, "runtime_data", None):
            runtime = cast("NascarConfigEntry", entry).runtime_data
            return tuple(runtime.reference.data.drivers.values())
    return demo_drivers() if provider == PROVIDER_DEMO else ()


def _driver_options(
    values: dict[str, Any], drivers: tuple[Driver, ...]
) -> list[selector.SelectOptionDict]:
    """Searchable labels include only known metadata, plus preserved selections."""
    options: dict[str, str] = {}
    for driver in sorted(
        drivers, key=lambda item: (item.name.casefold(), item.driver_id)
    ):
        details = [f"ID {driver.driver_id}"]
        if driver.series_ids:
            details.append(
                " / ".join(SERIES_NAMES[value] for value in driver.series_ids)
            )
        if driver.car_number is not None:
            details.append(f"#{driver.car_number}")
        else:
            for series_id in (1, 2, 3):
                association = driver.association_for(series_id)
                if association is not None and association.car_number is not None:
                    details.append(f"Series {series_id} #{association.car_number}")
        if driver.team is not None:
            details.append(driver.team)
        prefix = "Demo: " if values.get(CONF_PROVIDER) == PROVIDER_DEMO else ""
        options[str(driver.driver_id)] = f"{prefix}{driver.name} — {', '.join(details)}"
    selected = values.get(CONF_FAVORITE_DRIVERS, [])
    if isinstance(selected, list):
        for value in selected:
            if isinstance(value, str) and value.isascii() and value.isdecimal():
                options.setdefault(
                    value, f"NASCAR driver ID {value} (metadata unavailable)"
                )
    return [{"value": value, "label": label} for value, label in options.items()]


def _schema(
    values: dict[str, Any], drivers: tuple[Driver, ...] = ()
) -> probatio.Schema:
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
            probatio.Optional(
                CONF_FAVORITE_DRIVERS,
                # A validation default would reinsert the old IDs when the
                # frontend omits this optional field after clearing it.
                description={"suggested_value": values.get(CONF_FAVORITE_DRIVERS, [])},
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=_driver_options(values, drivers),
                    multiple=True,
                    custom_value=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
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
    favorites = values.get(CONF_FAVORITE_DRIVERS, [])
    try:
        if not isinstance(favorites, list):
            raise ValueError("Favorite drivers must be a list")
        normalize_favorite_driver_ids(favorites)
    except ValueError:
        return {CONF_FAVORITE_DRIVERS: "invalid_favorite_drivers"}
    return {}


def _normalized_input(values: dict[str, Any]) -> dict[str, Any]:
    """Store canonical IDs only when favorites were supplied by this form."""
    if CONF_FAVORITE_DRIVERS not in values:
        return values
    return {
        **values,
        CONF_FAVORITE_DRIVERS: [
            str(value)
            for value in normalize_favorite_driver_ids(values[CONF_FAVORITE_DRIVERS])
        ],
    }


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
            return self.async_create_entry(
                title=NAME, data=_normalized_input(user_input)
            )
        values = user_input or {}
        return self.async_show_form(
            step_id="user",
            # Source choices can change client-side before this form submits.
            # Names are offered in options only after the source is established,
            # so selecting CF never presents fictional demo drivers as real.
            data_schema=_schema(values),
            errors=errors,
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
        if user_input is not None:
            # HA's frontend can omit an emptied optional selector. Persist an
            # explicit empty override so entry.data cannot restore old favorites.
            user_input = {
                **user_input,
                CONF_FAVORITE_DRIVERS: user_input.get(CONF_FAVORITE_DRIVERS, []),
            }
        errors = _validate(user_input) if user_input is not None else {}
        if user_input is not None and not errors:
            return self.async_create_entry(title="", data=_normalized_input(user_input))
        values = {
            **self.config_entry.data,
            **self.config_entry.options,
            **(user_input or {}),
        }
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(
                values,
                _available_drivers(
                    self.config_entry, values.get(CONF_PROVIDER, PROVIDER_DEMO)
                ),
            ),
            errors=errors,
        )
