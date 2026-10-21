"""Synthetic normalized contract checks, including complete bounded pagination."""

import json
from dataclasses import replace

import pytest
from test_analytics import query, response, source
from test_history import KEY, fixture

from custom_components.nascar_race_center.analytics import analyze_history
from custom_components.nascar_race_center.dashboard_pages import (
    MAX_RESPONSE_BYTES,
    PageError,
    page,
    record_page,
)
from custom_components.nascar_race_center.dashboard_schema import project
from custom_components.nascar_race_center.history_models import (
    HistoryDataset,
    HistoryProvenance,
    HistoryResponse,
    HistoryResult,
    HistoryStatus,
)
from custom_components.nascar_race_center.history_parser import PARSERS


def historical(*datasets):
    return HistoryResponse(
        KEY,
        tuple(
            HistoryResult(
                HistoryStatus.AVAILABLE,
                HistoryProvenance(
                    k, KEY, "path_context_only", "fictional", "synthetic"
                ),
                PARSERS[k](fixture(k), KEY),
            )
            for k in datasets
        ),
    )


@pytest.mark.parametrize("kind", list(HistoryDataset))
def test_every_history_dataset_serializes_and_pages_without_loss(kind):
    result = historical(kind)
    complete = page(result, 0, 200, None)
    rows = []
    offset = 0
    token = None
    while True:
        current = page(result, offset, 1, token)
        rows.extend(current["records"])
        token = current["pagination"]["snapshot"]
        offset = current["pagination"]["next_offset"]
        if offset is None:
            break
    assert rows == complete["records"]
    assert len(rows) == complete["pagination"]["total"]
    assert complete["datasets"][0]["provenance"]["requested"]["race_id"] == "88001"
    json.dumps(complete, allow_nan=False)


def test_history_null_empty_identity_and_exact_run_namespaces():
    result = historical(HistoryDataset.WEEKEND, HistoryDataset.PITS)
    output = page(result, 0, 200, None)
    weekend = next(r for r in output["records"] if r["kind"] == "weekend")
    assert weekend["value"]["timing_run_id"] == "10"
    sessions = [r for r in output["records"] if r["kind"] == "session"]
    assert (
        sessions[0]["value"]["weekend_run_id"] != sessions[0]["value"]["timing_run_id"]
    )
    pit = next(r for r in output["records"] if r["kind"] == "pits")
    assert pit["value"]["nascar_driver_id"] is None
    assert "reported_numbers" in pit["value"]


def test_analytics_all_row_types_finite_values_and_snapshot_changes():
    history = historical(*HistoryDataset)
    result = analyze_history(history, query((99002,), last_lap=10))
    output = page(result, 0, 200, None)
    assert output["contract_version"] == 1
    assert output["query"]["driver_ids"] == ["99002"]
    assert "performance" in {r["kind"] for r in output["records"]}
    json.dumps(output, allow_nan=False)
    changed = replace(result, reason="changed")
    with pytest.raises(PageError, match="snapshot_changed"):
        page(changed, 1, 10, output["pagination"]["snapshot"])
    invalid = analyze_history(
        response(source(values=(float("nan"), 1, 2, 3, 4))), query()
    )
    json.dumps(page(invalid, 0, 200, None), allow_nan=False)
    assert project(float("inf")) is None
    with pytest.raises(ValueError, match="Unregistered"):
        project({"token": "must not escape"})


def test_large_record_stream_limits_bytes_without_losing_continuation():
    def rows():
        return ({"value": "x" * 2048, "index": i} for i in range(1000))

    output = record_page({}, rows(), 0, 200, None, "test")
    assert len(json.dumps(output).encode()) < MAX_RESPONSE_BYTES
    assert output["pagination"]["total"] == 1000
    assert 0 < output["pagination"]["returned"] < 200
    assert not output["pagination"]["complete"]
    next_page = record_page(
        {},
        rows(),
        output["pagination"]["next_offset"],
        200,
        output["pagination"]["snapshot"],
        "test",
    )
    assert next_page["records"][0]["index"] == len(output["records"])
    with pytest.raises(PageError, match="record_too_large"):
        record_page(
            {}, iter([{"value": "x" * MAX_RESPONSE_BYTES}]), 0, 200, None, "test"
        )
    with pytest.raises(PageError, match="invalid_offset"):
        record_page({}, iter([]), 1, 200, None, "test")
