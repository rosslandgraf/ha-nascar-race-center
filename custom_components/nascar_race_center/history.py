"""Stable consumer API for Phase 4B and Phase 5: runtime_data.history.

Explicit race + nonempty dataset selection only. No startup/periodic I/O,
automatic joins, persistent datasets, HTTP views, entities or analytics.
"""

import asyncio
from dataclasses import dataclass

from .history_models import (
    HistoricalRaceKey,
    HistoryDataset,
    HistoryProvenance,
    HistoryResponse,
    HistoryResult,
    HistoryStatus,
)
from .history_provider import HistoryProvider

MAX_IN_FLIGHT = 8


@dataclass(slots=True)
class _Flight:
    task: asyncio.Task[HistoryResult]
    waiters: int = 0


class HistoryService:
    """Entry-owned bounded request broker; no background prefetch or retry."""

    def __init__(
        self, provider: HistoryProvider, selected_series: tuple[int, ...]
    ) -> None:
        self.provider = provider
        self.selected_series = selected_series
        self._flights: dict[tuple[HistoricalRaceKey, HistoryDataset], _Flight] = {}
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    async def async_get(
        self, key: HistoricalRaceKey, datasets: tuple[HistoryDataset, ...]
    ) -> HistoryResponse:
        """Fetch requested datasets independently, preserving partial availability.

        Cancelling one waiter preserves other consumers. The last cancellation
        aborts its upstream task. Callers own returned immutable models; this
        service retains no normalized result after its last waiter returns.
        """
        if self._closed:
            raise RuntimeError("History service is closed")
        if (
            not isinstance(key, HistoricalRaceKey)
            or key.series_id not in self.selected_series
        ):
            raise ValueError("Select a monitored historical race")
        if (
            not isinstance(datasets, tuple)
            or not datasets
            or len(datasets) > len(HistoryDataset)
            or any(not isinstance(k, HistoryDataset) for k in datasets)
            or len(set(datasets)) != len(datasets)
        ):
            raise ValueError("Select distinct allowlisted historical datasets")
        results = await asyncio.gather(
            *(self._async_one(key, dataset) for dataset in datasets)
        )
        return HistoryResponse(key, tuple(results))

    async def _async_one(
        self, key: HistoricalRaceKey, dataset: HistoryDataset
    ) -> HistoryResult:
        flight_key = (key, dataset)
        flight = self._flights.get(flight_key)
        if flight is None:
            if len(self._flights) >= MAX_IN_FLIGHT:
                return HistoryResult(
                    HistoryStatus.NETWORK_ERROR,
                    HistoryProvenance(
                        dataset, key, "not_validated", "unverified_context", "deferred"
                    ),
                    reason="request_budget",
                )
            flight = _Flight(
                asyncio.create_task(self.provider.async_get_history(key, dataset))
            )
            self._flights[flight_key] = flight
        flight.waiters += 1
        try:
            return await asyncio.shield(flight.task)
        finally:
            flight.waiters -= 1
            if not flight.waiters:
                self._flights.pop(flight_key, None)
                if not flight.task.done():
                    flight.task.cancel()
                    await asyncio.gather(flight.task, return_exceptions=True)

    async def async_close(self, _: object = None) -> None:
        """Cancel/drain requests before releasing raw in-memory cache entries."""
        self._closed = True
        tasks = tuple(flight.task for flight in self._flights.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._flights.clear()
        self.provider.clear()
