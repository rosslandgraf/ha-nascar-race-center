"""Entry-owned on-demand analytics. No polling, transport routes or result cache."""

import asyncio
from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .analytics import analyze_history, unavailable_result
from .analytics_models import AnalyticsQuery, AnalyticsResult
from .history import HistoryService
from .history_models import HistoryDataset

MAX_ANALYTICS_IN_FLIGHT = 2
type _RequestKey = tuple[AnalyticsQuery, tuple[HistoryDataset, ...]]


@dataclass(slots=True)
class _Flight:
    task: asyncio.Task[AnalyticsResult]
    waiters: int = 0


class AnalyticsService:
    """Share identical consumers; retain executor slots until calculations finish."""

    def __init__(self, hass: HomeAssistant, history: HistoryService) -> None:
        self.hass = hass
        self.history = history
        self._closed = False
        self._flights: dict[_RequestKey, _Flight] = {}

    @property
    def closed(self) -> bool:
        return self._closed

    async def async_get(
        self, query: AnalyticsQuery, datasets: tuple[HistoryDataset, ...]
    ) -> AnalyticsResult:
        """Retrieve only explicit datasets through HistoryService, then calculate."""
        if self._closed:
            raise RuntimeError("Analytics service is closed")
        if (
            not isinstance(query, AnalyticsQuery)
            or query.key.series_id not in self.history.selected_series
            or not isinstance(datasets, tuple)
            or not datasets
            or len(datasets) > len(HistoryDataset)
            or any(not isinstance(k, HistoryDataset) for k in datasets)
            or len(set(datasets)) != len(datasets)
        ):
            raise ValueError("Select a monitored race and distinct historical datasets")
        key = (query, datasets)
        flight = self._flights.get(key)
        if flight is not None and flight.task.cancelling():
            return unavailable_result(query, "calculation_draining")
        if flight is None:
            if len(self._flights) >= MAX_ANALYTICS_IN_FLIGHT:
                return unavailable_result(query, "calculation_budget")
            flight = _Flight(
                asyncio.create_task(self._async_calculate(query, datasets))
            )
            self._flights[key] = flight

            def finished(
                _: asyncio.Task[AnalyticsResult], owned: _Flight = flight
            ) -> None:
                self._release(key, owned)

            flight.task.add_done_callback(finished)
        flight.waiters += 1
        try:
            return await asyncio.shield(flight.task)
        finally:
            flight.waiters -= 1
            if not flight.waiters:
                if not flight.task.done() and not flight.task.cancelling():
                    flight.task.cancel()
                if not flight.task.done():
                    await asyncio.gather(flight.task, return_exceptions=True)
                self._release(key, flight)

    def _release(self, key: _RequestKey, flight: _Flight) -> None:
        # Also runs after a repeatedly cancelled waiter abandoned its cleanup.
        if (
            not flight.waiters
            and flight.task.done()
            and self._flights.get(key) is flight
        ):
            self._flights.pop(key)

    async def _async_calculate(
        self, query: AnalyticsQuery, datasets: tuple[HistoryDataset, ...]
    ) -> AnalyticsResult:
        if self._closed:
            raise asyncio.CancelledError
        response = await self.history.async_get(query.key, datasets)
        if self._closed:
            raise asyncio.CancelledError
        # A Python executor cannot abort running pure code. Drain its bounded
        # job on cancellation before releasing this slot or completing unload.
        future = self.hass.async_add_executor_job(analyze_history, response, query)
        cancelled = False
        while True:
            try:
                result = await asyncio.shield(future)
                break
            except asyncio.CancelledError:
                if future.cancelled():
                    raise
                cancelled = True
        if cancelled:
            raise asyncio.CancelledError
        return result

    async def async_close(self, _: object = None) -> None:
        """Close entry consumers and drain pure workers; HistoryService owns I/O."""
        self._closed = True
        tasks = tuple(f.task for f in self._flights.values())
        for task in tasks:
            if not task.cancelling():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._flights.clear()
