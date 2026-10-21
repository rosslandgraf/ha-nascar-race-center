"""Bound and align normalized history before any calculation or cross-feed row."""

from collections.abc import Iterable
from math import isfinite

from .analytics_models import AnalyticsQuery, DatasetEvidence
from .history_models import (
    HistoricalData,
    HistoricalResult,
    HistoryDataset,
    HistoryResponse,
    HistoryStatus,
    ReportedMetric,
)
from .history_parser import AVERAGE_FIELDS, LOOP_INTS
from .scoring import StageResult


def identity(value: object) -> bool:
    return type(value) is int and 1 <= value <= 10**10


def valid_time(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
        and value > 0
    )


def position(value: object) -> int | None:
    # At most 100 source drivers; 0, -1, 999 are not usable ordinal positions.
    return value if type(value) is int and 1 <= value <= 100 else None


def _unique(ids: Iterable[int]) -> None:
    seen: set[int] = set()
    for value in ids:
        if not identity(value) or value in seen:
            raise ValueError("driver_identity")
        seen.add(value)


def _results(rows: tuple[HistoricalResult, ...] | None) -> None:
    if rows is None:
        return
    if len(rows) > 100:
        raise ValueError("resource_limit")
    _unique(r.driver.nascar_driver_id for r in rows)
    runs = {r.results_run_id for r in rows if r.results_run_id is not None}
    if len(runs) > 1 or any(not identity(r) for r in runs):
        raise ValueError("conflicting_results_run")


def _stage_rows(rows: tuple[StageResult, ...]) -> None:
    if len(rows) > 100:
        raise ValueError("resource_limit")
    _unique(r.driver_id for r in rows)


def _metrics(rows: tuple[ReportedMetric, ...], fields: tuple[str, ...]) -> None:
    if len(rows) > len(fields) or len({r.field for r in rows}) != len(rows):
        raise ValueError("metric_identity")
    for row in rows:
        if row.field not in fields or row.interpretation not in (
            "reported",
            "missing",
            "candidate_sentinel",
        ):
            raise ValueError("unsupported_metric")
        if row.value is not None and (
            type(row.value) not in (int, float)
            or not isfinite(row.value)
            or abs(row.value) > 10**12
        ):
            raise ValueError("invalid_reported_number")


def _validate(
    data: HistoricalData, kind: HistoryDataset, query: AnalyticsQuery
) -> None:
    if kind == HistoryDataset.LAPS:
        if len(data.laps) > 100 or sum(len(d.laps) for d in data.laps) > 50000:
            raise ValueError("resource_limit")
        _unique(d.driver.nascar_driver_id for d in data.laps)
        for driver in data.laps:
            if len(driver.laps) > 5000:
                raise ValueError("resource_limit")
            seen: set[int] = set()
            for lap in driver.laps:
                if (
                    type(lap.lap) is not int
                    or not 0 <= lap.lap <= 10**10
                    or lap.lap in seen
                ):
                    raise ValueError("duplicate_or_invalid_driver_lap")
                seen.add(lap.lap)
    elif kind == HistoryDataset.WEEKEND and data.weekend is not None:
        weekend = data.weekend
        if weekend.key != query.key:
            raise ValueError("race_identity")
        _results(weekend.results)
        if len(weekend.sessions or ()) > 30 or len(weekend.stages or ()) > 20:
            raise ValueError("resource_limit")
        _unique(s.weekend_run_id for s in weekend.sessions or ())
        for session in weekend.sessions or ():
            _results(session.results)
        _unique(s.number for s in weekend.stages or ())
        for stage in weekend.stages or ():
            _stage_rows(stage.results)
    elif kind == HistoryDataset.STAGES:
        if len(data.stages) > 20:
            raise ValueError("resource_limit")
        _unique(s.number for s in data.stages)
        runs: set[int | None] = set()
        for archived_stage in data.stages:
            ctx = archived_stage.context
            if (
                ctx.race_id != query.key.race_id
                or ctx.series_id not in (None, query.key.series_id)
                or ctx.season not in (None, query.key.season)
                or ctx.run_namespace != "stage_run"
                or not identity(ctx.run_id)
            ):
                raise ValueError("stage_context")
            runs.add(ctx.run_id)
            _stage_rows(archived_stage.results)
        if len(runs) > 1:
            raise ValueError("conflicting_stage_run")
    elif kind == HistoryDataset.LOOP:
        if len(data.loops) > 1:
            raise ValueError("resource_limit")
        for loop in data.loops:
            if len(loop.drivers) > 100:
                raise ValueError("resource_limit")
            _unique(d.nascar_driver_id for d in loop.drivers)
            for row in loop.drivers:
                _metrics(row.metrics, (*LOOP_INTS, "avg_ps", "rating"))
    elif kind == HistoryDataset.AVERAGES:
        if len(data.averages) > 30:
            raise ValueError("resource_limit")
        for group in data.averages:
            if len(group.drivers) > 100 or (
                group.title is not None and len(group.title) > 2048
            ):
                raise ValueError("resource_limit")
            _unique(d.driver.nascar_driver_id for d in group.drivers)
            for average_driver in group.drivers:
                _metrics(average_driver.metrics, AVERAGE_FIELDS)


def align_history(
    response: HistoryResponse, query: AnalyticsQuery
) -> tuple[dict[HistoryDataset, HistoricalData], tuple[DatasetEvidence, ...]]:
    """Invalid peers fail independently; never borrow a race or run identity."""
    usable: dict[HistoryDataset, HistoricalData] = {}
    evidence: list[DatasetEvidence] = []
    if len(response.results) > len(HistoryDataset):
        return {}, (
            DatasetEvidence(
                HistoryDataset.LAPS, HistoryStatus.INVALID, None, "resource_limit"
            ),
        )
    kinds = [r.provenance.dataset for r in response.results]
    for result in response.results:
        p = result.provenance
        reason = None
        if response.key != query.key or p.requested != query.key:
            reason = "race_identity"
        elif kinds.count(p.dataset) != 1:
            reason = "duplicate_dataset"
        elif result.status in (HistoryStatus.AVAILABLE, HistoryStatus.EMPTY):
            if p.validation not in (
                "reported_identity",
                "path_context_only",
                "fictional",
            ):
                reason = "unvalidated_source"
            elif result.data is None:
                reason = "missing_normalized_data"
            elif result.status == HistoryStatus.EMPTY and not result.data.empty:
                reason = "inconsistent_empty_status"
            else:
                try:
                    _validate(result.data, p.dataset, query)
                except ValueError as error:
                    reason = str(error)
                else:
                    usable[p.dataset] = result.data
        evidence.append(
            DatasetEvidence(
                p.dataset,
                HistoryStatus.INVALID if reason else result.status,
                p,
                reason or result.reason,
            )
        )
    return usable, tuple(evidence)
