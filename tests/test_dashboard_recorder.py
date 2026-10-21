"""Actual Recorder remains unchanged by dashboard reads and subscriptions."""

from homeassistant.components.recorder.db_schema import States
from pytest_homeassistant_custom_component.components.recorder.common import (
    async_wait_recording_done,
)
from sqlalchemy import func, select
from test_analytics_runtime import (
    mock_recorder_before_hass as mock_recorder_before_hass,
)
from test_analytics_runtime import setup_demo
from test_dashboard_websocket import call, receive_update


async def test_dashboard_reads_add_zero_recorder_rows(
    recorder_mock, hass, hass_ws_client
):
    entry = await setup_demo(hass)
    client = await hass_ws_client(hass)
    await hass.async_block_till_done()

    def count():
        with recorder_mock.get_session() as session:
            return session.scalar(select(func.count(States.state_id)))

    await async_wait_recording_done(hass)
    before = await hass.async_add_executor_job(count)
    assert before > 0
    assert (await call(client, entry, "subscribe_live", series_id=1))["success"]
    await receive_update(client)
    history_token = analytics_token = None
    for _ in range(5):
        assert (await call(client, entry, "bootstrap"))["success"]
        assert (await call(client, entry, "live", series_id=1))["success"]
        history = await call(
            client,
            entry,
            "history",
            series_id=1,
            season=2024,
            race_id=88001,
            datasets=["weekend"],
            **({"snapshot": history_token} if history_token else {}),
        )
        assert history["success"]
        history_token = history["result"]["data"]["pagination"]["snapshot"]
        analytics = await call(
            client,
            entry,
            "analytics",
            series_id=1,
            season=2024,
            race_id=88001,
            datasets=["weekend"],
            driver_ids=[99002],
            first_lap=1,
            last_lap=10,
            windows=[5],
            time_basis="all_available",
            **({"snapshot": analytics_token} if analytics_token else {}),
        )
        assert analytics["success"]
        analytics_token = analytics["result"]["data"]["pagination"]["snapshot"]
    await async_wait_recording_done(hass)
    assert await hass.async_add_executor_job(count) == before
