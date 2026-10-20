"""Exercise real entity state writes, routing and missing values in Home Assistant."""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nascar_race_center.const import (
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_DEMO,
)
from custom_components.nascar_race_center.models import LiveSnapshot, Race


def entity_state(
    hass: HomeAssistant, entry: MockConfigEntry, series: int, key: str
) -> State:
    """Find an entity through its persisted unique ID, independent of display names."""
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_{series}_{key}"
    )
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    return state


async def test_live_metadata_routes_only_to_reported_series(
    hass: HomeAssistant,
) -> None:
    """Global Cup data must never appear as Truck timing or fabricated zeros."""
    now = dt_util.utcnow()
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=())
    provider.async_get_live = AsyncMock(
        return_value=LiveSnapshot(
            1, 123, status="running", flag="yellow", lap=42, source_updated_at=now
        )
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: ["1", "3"]},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entity_state(hass, entry, 1, "current_lap").state == "42"
    assert entity_state(hass, entry, 1, "flag").state == "yellow"
    assert entity_state(hass, entry, 1, "race_status").state == "running"
    assert entity_state(hass, entry, 3, "race_status").state == "not_reported"
    assert entity_state(hass, entry, 3, "feed_status").state == "not_reported"
    assert entity_state(hass, entry, 3, "current_lap").state == STATE_UNAVAILABLE
    assert entity_state(hass, entry, 3, "flag").state == STATE_UNAVAILABLE
    provider.async_get_live.assert_awaited_once()


async def test_missing_values_are_unknown_and_no_race_is_not_an_outage(
    hass: HomeAssistant,
) -> None:
    """Successful feeds with absent optional fields preserve unknown states."""
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=())
    provider.async_get_live = AsyncMock(return_value=LiveSnapshot(1, 123))
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: ["1"]},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entity_state(hass, entry, 1, "current_lap").state == STATE_UNKNOWN
    assert entity_state(hass, entry, 1, "flag").state == STATE_UNKNOWN
    assert entity_state(hass, entry, 1, "feed_status").state == "freshness_unknown"
    assert entity_state(hass, entry, 1, "next_race").state == STATE_UNKNOWN
    assert entity_state(hass, entry, 1, "next_race_start").state == STATE_UNKNOWN
    assert entity_state(hass, entry, 1, "scheduled_races").state == "0"
    binary_id = er.async_get(hass).async_get_entity_id(
        "binary_sensor", DOMAIN, f"{entry.entry_id}_1_feed_stale"
    )
    assert binary_id is not None
    assert hass.states.get(binary_id).state == STATE_UNKNOWN


async def test_stale_feed_is_visible_and_schedule_remains_usable(
    hass: HomeAssistant,
) -> None:
    """Archived live data must not be presented as current race timing."""
    now = dt_util.utcnow()
    race = Race(1, 123, "Synthetic future race", now + timedelta(days=1), "Test track")
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=(race,))
    provider.async_get_live = AsyncMock(
        return_value=LiveSnapshot(
            1,
            120,
            flag="green",
            lap=100,
            source_updated_at=now - timedelta(days=1),
        )
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: ["1"]},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entity_state(hass, entry, 1, "feed_status").state == "stale"
    assert entity_state(hass, entry, 1, "race_status").state == "stale"
    assert entity_state(hass, entry, 1, "current_lap").state == STATE_UNAVAILABLE
    assert entity_state(hass, entry, 1, "next_race").state == race.name
    start = entity_state(hass, entry, 1, "next_race_start")
    assert dt_util.parse_datetime(start.state) == race.start_time.replace(microsecond=0)
    assert start.attributes["race_id"] == 123
    assert start.attributes["track"] == "Test track"
    assert "races" not in start.attributes
    assert len(start.attributes) < 10


async def test_next_race_advances_at_start_without_network_poll(
    hass: HomeAssistant,
) -> None:
    """Clock progression updates next-race entities even during a slow poll window."""
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    now = dt_util.utcnow()
    first = Race(1, 1, "First synthetic race", now + timedelta(minutes=1))
    second = Race(1, 2, "Second synthetic race", now + timedelta(days=1))
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=(first, second))
    provider.async_get_live = AsyncMock(return_value=None)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: ["1"]},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entity_state(hass, entry, 1, "next_race").state == first.name
    provider.async_get_schedule.reset_mock()
    after_start = now + timedelta(minutes=1, seconds=2)
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=after_start,
    ):
        async_fire_time_changed(hass, after_start)
        await hass.async_block_till_done()
    assert entity_state(hass, entry, 1, "next_race").state == second.name
    provider.async_get_schedule.assert_not_awaited()


async def test_live_source_expires_locally_without_another_provider_request(
    hass: HomeAssistant,
) -> None:
    """A long poll interval must never leave old timing presented as current."""
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    now = dt_util.utcnow().replace(microsecond=0)
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=())
    # Lap zero is a valid reported value and does not establish active racing,
    # so the conservative off-season interval remains longer than source expiry.
    provider.async_get_live = AsyncMock(
        return_value=LiveSnapshot(
            1, 10, status="race", flag="green", lap=0, source_updated_at=now
        )
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: ["1"]},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.runtime_data.live.update_interval >= timedelta(hours=6)
    assert entity_state(hass, entry, 1, "current_lap").state == "0"
    assert entity_state(hass, entry, 1, "feed_status").state == "ok"
    stale_id = er.async_get(hass).async_get_entity_id(
        "binary_sensor", DOMAIN, f"{entry.entry_id}_1_feed_stale"
    )
    assert stale_id is not None
    assert hass.states.get(stale_id).state == "off"
    provider.async_get_live.reset_mock()
    expired = now + timedelta(minutes=16)
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=expired,
    ):
        async_fire_time_changed(hass, expired)
        await hass.async_block_till_done()
    assert entity_state(hass, entry, 1, "current_lap").state == STATE_UNAVAILABLE
    assert entity_state(hass, entry, 1, "flag").state == STATE_UNAVAILABLE
    assert entity_state(hass, entry, 1, "feed_status").state == "stale"
    assert hass.states.get(stale_id).state == "on"
    provider.async_get_live.assert_not_awaited()


async def test_unload_cleans_up_armed_live_source_expiry_timer(
    hass: HomeAssistant,
) -> None:
    """A source-expiry timer must not survive a normal config-entry unload."""
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=())
    provider.async_get_live = AsyncMock(
        return_value=LiveSnapshot(
            1, 10, flag="green", lap=0, source_updated_at=dt_util.utcnow()
        )
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: ["1"]},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entity_state(hass, entry, 1, "feed_status").state == "ok"
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    # The Home Assistant fixture's normal cleanup check rejects lingering timers;
    # no test-only coordinator shutdown or timer cancellation is used here.
