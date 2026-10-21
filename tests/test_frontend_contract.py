"""Export/recheck fictional browser inputs through the real v1 serializers.

Regenerate explicitly with NRC_EXPORT_FRONTEND=1 pytest -q
 tests/test_frontend_contract.py. No NASCAR I/O or fixture use in the card bundle.
"""

import json
import math
import os
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import AsyncMock

import test_dashboard_websocket as backend
from test_analytics import query, response, source
from test_dashboard import historical
from test_scoring import embedded_payload

from custom_components.nascar_race_center.analytics import analyze_history
from custom_components.nascar_race_center.dashboard_pages import page
from custom_components.nascar_race_center.history_models import HistoryDataset

dashboard_entry = backend.dashboard_entry

FIXTURE = Path(__file__).parents[1] / "frontend/demo/contract.json"


def schema(value):
    """Capture keys/types/variants, allowing times and synthetic values to change."""
    if isinstance(value, dict):
        return {k: schema(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return sorted({json.dumps(schema(v), sort_keys=True) for v in value})
    return type(value).__name__


async def test_frontend_fictional_contract(hass, dashboard_entry, hass_ws_client):
    client = await hass_ws_client(hass)
    payload = embedded_payload()
    prototype = payload["vehicles"][0]
    vehicles = []
    for i in range(16):
        vehicle = deepcopy(prototype)
        vehicle.update(
            driver={
                "driver_id": 99001 + i,
                "full_name": f"Fictional Driver {chr(65 + i)}",
            },
            vehicle_number=f"{i + 1:02}",
            running_position=i + 1,
            starting_position=(i + 4) % 16 + 1,
            delta=round(i * 0.72, 3),
            last_lap_time=round(31.0 + i * 0.07, 3),
            best_lap_time=round(30.5 + i * 0.04, 3),
        )
        vehicles.append(vehicle)
    backend.set_live(dashboard_entry, vehicles=vehicles, run_name="Fictional 300")
    output = {}
    for command, kwargs in (
        ("bootstrap", {}),
        ("live", {"series_id": 1}),
        ("schedule", {"series_id": 1, "limit": 200}),
        (
            "live_driver",
            {"series_id": 1, "driver_id": 99002, "collection": "pit_stops"},
        ),
        ("live_scoring", {"series_id": 1, "collection": "points"}),
    ):
        wire = await backend.call(client, dashboard_entry, command, **kwargs)
        assert wire["success"]
        wire["result"]["entry_id"] = "FICTIONAL_ENTRY"
        output[command] = wire["result"]
    original = historical(*HistoryDataset)
    # 48 observations and a missing/null interval exercise chart gaps. Computation
    # uses the actual Phase 4B model/function, never a browser-recreated formula.
    lap_data = response(
        *(
            source(
                driver_id=99002 + i,
                values=tuple(
                    None
                    if lap in (17, 18)
                    else round(31 + i * 0.23 + math.sin(lap / 4) * 0.4, 3)
                    for lap in range(1, 49)
                ),
                positions=[i + 1 + (lap // 12 % 2) for lap in range(48)],
            )
            for i in range(2)
        )
    ).results[0]
    original = replace(
        original,
        results=tuple(
            lap_data if r.provenance.dataset == HistoryDataset.LAPS else r
            for r in original.results
        ),
    )
    dashboard_entry.runtime_data.history.async_get = AsyncMock(return_value=original)
    wire = await backend.call(
        client,
        dashboard_entry,
        "history",
        series_id=1,
        season=2024,
        race_id=88001,
        datasets=list(HistoryDataset),
        limit=200,
    )
    assert wire["success"]
    wire["result"]["entry_id"] = "FICTIONAL_ENTRY"
    output["history"] = wire["result"]
    analytical = analyze_history(
        original, query((99002, 99003), last_lap=48, windows=(5,))
    )
    # Store the entire normalized stream as fixture input, then the browser mock
    # applies real 200-record page boundaries. This is never bundled at runtime.
    analytical_page = page(analytical, 0, 200, None)
    all_rows = list(analytical_page["records"])
    while analytical_page["pagination"]["next_offset"] is not None:
        analytical_page = page(
            analytical,
            analytical_page["pagination"]["next_offset"],
            200,
            analytical_page["pagination"]["snapshot"],
        )
        all_rows.extend(analytical_page["records"])
    analytical_page["records"] = all_rows
    output["analytics"] = {
        "api_version": 1,
        "entry_id": "FICTIONAL_ENTRY",
        "data": analytical_page,
    }
    for envelope in output.values():
        p = envelope["data"].get("pagination")
        if p:
            p["snapshot"] = "a" * 64
    if os.environ.get("NRC_EXPORT_FRONTEND") == "1":
        FIXTURE.write_text(json.dumps(output, indent=2) + "\n")
    assert schema(json.loads(json.dumps(output))) == schema(
        json.loads(FIXTURE.read_text())
    )
