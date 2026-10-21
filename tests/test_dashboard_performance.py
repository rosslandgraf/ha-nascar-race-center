"""Synthetic resource/delivery observations; never a NASCAR latency claim."""

import json
import time
import tracemalloc
from dataclasses import replace

from test_dashboard_websocket import call, receive_update, set_live
from test_init import demo_entry

from custom_components.nascar_race_center.analytics import analyze_history
from custom_components.nascar_race_center.analytics_models import AnalyticsQuery
from custom_components.nascar_race_center.dashboard_pages import (
    MAX_RESPONSE_BYTES,
)
from custom_components.nascar_race_center.dashboard_snapshots import build_index
from custom_components.nascar_race_center.history_models import (
    DriverLaps,
    HistoricalData,
    HistoricalDriver,
    HistoricalLap,
    HistoricalRaceKey,
    HistoryDataset,
    HistoryProvenance,
    HistoryResponse,
    HistoryResult,
    HistoryStatus,
)


def test_largest_synthetic_pages_have_bounded_retention_and_bytes():
    key = HistoricalRaceKey(2024, 1, 88001)
    history = HistoryResponse(
        key,
        (
            HistoryResult(
                HistoryStatus.AVAILABLE,
                HistoryProvenance(
                    HistoryDataset.LAPS, key, "fictional", "fictional", "synthetic"
                ),
                HistoricalData(
                    laps=tuple(
                        DriverLaps(
                            HistoricalDriver(i + 1),
                            None,
                            tuple(
                                HistoricalLap(lap, float(30 + lap % 10), None, 1 + i)
                                for lap in range(1, 5001)
                            ),
                        )
                        for i in range(10)
                    )
                ),
            ),
        ),
    )
    analytics = analyze_history(
        history,
        AnalyticsQuery(key, tuple(range(1, 9)), 1, 1250, (5, 10, 15, 20, 25, 30)),
    )
    observations = {}
    for label, result in (
        ("history_50000_laps", history),
        ("analytics_60000_projected_windows", analytics),
    ):
        start = time.perf_counter()
        index = build_index(result)
        first_seconds = time.perf_counter() - start
        start = time.perf_counter()
        output = index.page("a" * 64, 0, 200)
        first_read_seconds = time.perf_counter() - start
        start = time.perf_counter()
        later = index.page("a" * 64, 200, 200)
        next_seconds = time.perf_counter() - start
        assert later["records"] != output["records"]
        tracemalloc.start()
        traced_index = build_index(result)
        retained, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert traced_index.retained_bytes >= retained
        size = len(json.dumps(output).encode())
        assert size < MAX_RESPONSE_BYTES
        assert output["pagination"]["returned"] == 200
        assert output["pagination"]["next_offset"] == 200
        observations[label] = {
            "first_build_seconds": first_seconds,
            "first_read_seconds": first_read_seconds,
            "next_read_seconds": next_seconds,
            "budgeted_bytes": index.retained_bytes,
            "retained_bytes": retained,
            "peak_bytes": peak,
            "response_bytes": size,
            "total_records": output["pagination"]["total"],
        }
    assert observations["history_50000_laps"]["total_records"] == 50010
    print("DASHBOARD_PAGE_MEASUREMENTS=" + json.dumps(observations))


async def test_synthetic_hundred_driver_update_delivery(hass, hass_ws_client):
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    snapshot = set_live(entry)
    board = snapshot.leaderboard
    drivers = tuple(
        replace(board.drivers[0], driver_id=i + 1, position=i + 1) for i in range(100)
    )
    snapshot = replace(
        snapshot, leaderboard=replace(board, drivers=drivers, reported_count=100)
    )
    entry.runtime_data.live.async_set_updated_data(snapshot)
    client = await hass_ws_client(hass)
    await call(client, entry, "subscribe_live", series_id=1)
    initial = await receive_update(client)
    assert len(initial["leaderboard"]) == 100
    delays = []
    for lap in range(100, 105):
        start = time.perf_counter()
        entry.runtime_data.live.async_set_updated_data(replace(snapshot, lap=lap))
        output = await receive_update(client)
        delays.append(time.perf_counter() - start)
        assert output["session"]["lap"] == lap
    print(
        "DASHBOARD_DELIVERY_MEASUREMENTS="
        + json.dumps(
            {
                "seconds": delays,
                "hundred_driver_payload_bytes": len(json.dumps(initial).encode()),
            }
        )
    )
