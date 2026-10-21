"""Bounded record pages for large history/analytics results, run in HA executor."""

import json
from collections.abc import Iterator
from hashlib import sha256
from typing import Any

from .analytics_models import AnalyticsResult
from .dashboard_schema import fields, project
from .history_models import HistoryResponse

MAX_RESPONSE_BYTES = 256 * 1024
MAX_PAGE_RECORDS = 200


class PageError(ValueError):
    """Safe stable transport error code, never source exception text."""


def history_records(response: HistoryResponse) -> Iterator[dict[str, Any]]:
    """Flatten collections at row boundaries, retaining parents and source order."""
    value: object
    for result in response.results:
        data = result.data
        if data is None:
            continue
        dataset = result.provenance.dataset

        def row(
            kind: str, value: object, dataset: str = dataset, **context: object
        ) -> dict[str, Any]:
            return {
                "dataset": dataset,
                "kind": kind,
                **context,
                "value": project(value),
            }

        w = data.weekend
        if w is not None:
            yield {
                "dataset": dataset,
                "kind": "weekend",
                "value": fields(
                    w,
                    (
                        "key name track_id track_name timing_run_id scheduled_laps "
                        "actual_laps scheduled_distance actual_distance "
                        "date_scheduled_reported race_date_reported inspection_complete"
                        " master_race_id race_type_code"
                    ),
                ),
                "collections": {
                    key: getattr(w, key) is not None
                    for key in (
                        "results",
                        "sessions",
                        "leaders",
                        "cautions",
                        "stages",
                        "schedule",
                    )
                },
            }
            for value in w.results or ():
                yield row("result", value)
            for session in w.sessions or ():
                yield {
                    "dataset": dataset,
                    "kind": "session",
                    "value": fields(
                        session,
                        "weekend_run_id timing_run_id run_type_code name "
                        "run_date run_date_utc",
                    ),
                    "results_available": session.results is not None,
                }
                for value in session.results or ():
                    yield row(
                        "session_result",
                        value,
                        weekend_run_id=str(session.weekend_run_id),
                    )
            for kind in ("leaders", "cautions", "schedule"):
                for value in getattr(w, kind) or ():
                    yield row(kind, value)
            for stage in w.stages or ():
                yield {
                    "dataset": dataset,
                    "kind": "weekend_stage",
                    "number": stage.number,
                    "result_count": len(stage.results),
                }
                for value in stage.results:
                    yield row("weekend_stage_result", value, number=stage.number)
        for driver in data.laps:
            yield {
                "dataset": dataset,
                "kind": "lap_driver",
                "value": fields(driver, "driver running_position"),
                "lap_count": len(driver.laps),
            }
            for index, value in enumerate(driver.laps):
                yield row(
                    "lap",
                    value,
                    driver_id=str(driver.driver.nascar_driver_id),
                    source_index=index,
                )
        for kind in ("flags", "notes", "pits"):
            for value in getattr(data, kind):
                yield row(kind, value)
        for index, group in enumerate(data.loops):
            yield {
                "dataset": dataset,
                "kind": "loop",
                "source_index": index,
                "value": fields(group, "name scheduled_laps actual_laps"),
                "driver_count": len(group.drivers),
            }
            for value in group.drivers:
                yield row("loop_driver", value, source_index=index)
        for index, average_group in enumerate(data.averages):
            yield {
                "dataset": dataset,
                "kind": "average",
                "source_index": index,
                "title": average_group.title,
                "driver_count": len(average_group.drivers),
            }
            for value in average_group.drivers:
                yield row("average_driver", value, source_index=index)
        for archived_stage in data.stages:
            yield {
                "dataset": dataset,
                "kind": "stage",
                "context": project(archived_stage.context),
                "number": archived_stage.number,
                "result_count": len(archived_stage.results),
            }
            for value in archived_stage.results:
                yield row(
                    "stage_result",
                    value,
                    context=project(archived_stage.context),
                    number=archived_stage.number,
                )


def analytics_records(result: AnalyticsResult) -> Iterator[dict[str, Any]]:
    for driver in result.drivers:
        identity = {"driver_id": str(driver.driver_id)}
        yield {
            "kind": "driver",
            **identity,
            "value": fields(driver, "status reason coverage metrics fastest_lap"),
        }
        for name in ("samples", "gaps", "consecutive_runs"):
            for value in getattr(driver, name):
                yield {"kind": name, **identity, "value": project(value)}
        for series in driver.rolling:
            yield {
                "kind": "window_summary",
                **identity,
                "size": series.size,
                "best_mean": project(series.best_mean),
            }
            for value in series.windows:
                yield {
                    "kind": "window",
                    **identity,
                    "size": series.size,
                    "value": project(value),
                }
        yield {
            "kind": "position_summary",
            **identity,
            "value": fields(
                driver.positions, "start end change best worst first_position_samples"
            ),
        }
        for name in ("points", "gaps"):
            for value in getattr(driver.positions, name):
                yield {"kind": f"position_{name}", **identity, "value": project(value)}
    for comparison in result.comparisons:
        yield {"kind": "comparison", "value": project(comparison)}
    for performance in result.performance:
        yield {
            "kind": "performance",
            "driver_id": str(performance.driver_id),
            "value": fields(
                performance,
                (
                    "result result_reason start_finish_position_change "
                    "reported_position_difference"
                ),
            ),
        }
        for name in ("stages", "reported_metrics", "sessions"):
            for value in getattr(performance, name):
                yield {
                    "kind": f"performance_{name}",
                    "driver_id": str(performance.driver_id),
                    "value": project(value),
                }


def page(
    result: HistoryResponse | AnalyticsResult,
    offset: int,
    limit: int,
    snapshot: str | None,
) -> dict[str, Any]:
    """Bound memory/bytes, hash all rows to reject mixed snapshots on continuation.

    No completed-result cache: the existing history/analytics brokers own I/O,
    coalescing and cancellation. Continuations may recalculate from cached data.
    """
    if isinstance(result, HistoryResponse):
        header = {
            "race": project(result.key),
            "status": result.status,
            "datasets": [
                {
                    "status": item.status,
                    "reason": item.reason,
                    "classification": item.classification,
                    "provenance": project(item.provenance),
                }
                for item in result.results
            ],
        }
        records = history_records(result)
        # Retrieval/delivery metadata varies on cache hits; hash semantic context.
        context: object = [
            project(result.key),
            [
                (
                    r.status,
                    r.reason,
                    r.provenance.validation,
                    r.provenance.coverage,
                    r.provenance.dataset,
                )
                for r in result.results
            ],
        ]
    else:
        header = fields(
            result,
            (
                "contract_version query status reason evidence race_metrics "
                "caveats race_timing_run_id"
            ),
        )
        records = analytics_records(result)
        context = [
            project(result.query),
            result.status,
            result.reason,
            [(e.dataset, e.status, e.reason) for e in result.evidence],
        ]
    return record_page(header, records, offset, limit, snapshot, context)


def record_page(
    header: dict[str, Any],
    records: Iterator[dict[str, Any]],
    offset: int,
    limit: int,
    snapshot: str | None,
    context: object,
) -> dict[str, Any]:
    """Shared finite record stream protocol for schedules and live details too."""
    digest = sha256(json.dumps(context, allow_nan=False).encode())
    rows: list[dict[str, Any]] = []
    used = len(json.dumps(header, allow_nan=False).encode()) + 2048
    total = 0
    full = False
    for index, record in enumerate(records):
        encoded = json.dumps(record, ensure_ascii=True, allow_nan=False).encode()
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        total += 1
        if index < offset or full:
            continue
        if used + len(encoded) > MAX_RESPONSE_BYTES:
            if not rows:
                raise PageError("record_too_large")
            full = True
            continue
        rows.append(record)
        used += len(encoded) + 1
        full = len(rows) >= limit
    token = digest.hexdigest()
    if snapshot is not None and snapshot != token:
        raise PageError("snapshot_changed")
    if offset > total:
        raise PageError("invalid_offset")
    next_offset = offset + len(rows)
    return {
        **header,
        "records": rows,
        "pagination": {
            "offset": offset,
            "limit": limit,
            "returned": len(rows),
            "total": total,
            "next_offset": next_offset if next_offset < total else None,
            "snapshot": token,
            "complete": next_offset == total,
        },
    }
