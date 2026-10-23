"""Independent on-demand history providers; no coordinator or polling loops."""

from collections import OrderedDict
from dataclasses import replace
from typing import Literal, Protocol

from .api import NascarApiClient
from .endpoints import historical_path
from .history_models import (
    HistoricalRaceKey,
    HistoryDataset,
    HistoryProvenance,
    HistoryResult,
    HistoryStatus,
)
from .history_parser import PARSERS
from .models import ProviderError, SchemaError

HISTORY_TTL = 3600


class HistoryProvider(Protocol):
    async def async_get_history(
        self, key: HistoricalRaceKey, dataset: HistoryDataset
    ) -> HistoryResult:
        """Read exactly one explicitly requested dataset."""
        ...

    def clear(self) -> None:
        """Release ephemeral historical response memory."""
        ...


class CFHistoryProvider:
    """Use the entry's transport, host throttles and isolated history cache."""

    def __init__(self, api: NascarApiClient) -> None:
        self.api = api
        self.dataset_diagnostics: OrderedDict[
            tuple[HistoricalRaceKey, HistoryDataset], dict[str, object]
        ] = OrderedDict()

    def _result(self, result: HistoryResult) -> HistoryResult:
        provenance = result.provenance
        key = (provenance.requested, provenance.dataset)
        self.dataset_diagnostics[key] = {
            "season": provenance.requested.season,
            "series_id": provenance.requested.series_id,
            "race_id": provenance.requested.race_id,
            "dataset": provenance.dataset.value,
            "status": result.status.value,
            "http_status": provenance.http_status,
            "reason": result.reason,
        }
        self.dataset_diagnostics.move_to_end(key)
        while len(self.dataset_diagnostics) > 24:
            self.dataset_diagnostics.popitem(last=False)
        return result

    def clear(self) -> None:
        self.api.clear_history()
        self.dataset_diagnostics.clear()

    async def async_get_history(
        self, key: HistoricalRaceKey, dataset: HistoryDataset
    ) -> HistoryResult:
        path = historical_path(key, dataset)
        observed = (
            key == HistoricalRaceKey(2026, 1, 5626)
            if dataset == HistoryDataset.PITS
            else key == HistoricalRaceKey(2024, 1, 5392)
        )
        provenance = HistoryProvenance(
            dataset,
            key,
            "not_validated",
            "observed_example" if observed else "unverified_context",
            "not_attempted",
        )
        try:
            payload = await self.api.async_get_json(
                path, minimum_ttl=HISTORY_TTL, minimum_interval=60
            )
            try:
                data = PARSERS[dataset](payload, key)
            except ValueError, TypeError, OverflowError, RecursionError:
                self.api.discard_history(path)
                return self._result(
                    HistoryResult(
                        HistoryStatus.INVALID,
                        self._metadata(path, provenance),
                        reason="schema_or_identity",
                    )
                )
        except ProviderError as error:
            # 404 alone cannot distinguish never supported from not yet published.
            status = (
                HistoryStatus.INVALID
                if isinstance(error, SchemaError)
                else HistoryStatus.UNVERIFIED
                if error.status in (404, 410)
                else HistoryStatus.NETWORK_ERROR
            )
            provenance = replace(
                self._metadata(path, provenance),
                http_status=error.status,
                retry_after=error.retry_after,
            )
            return self._result(
                HistoryResult(
                    status,
                    provenance,
                    reason="not_found_publication_unknown"
                    if error.status in (404, 410)
                    else "invalid_json_or_size"
                    if isinstance(error, SchemaError)
                    else "access_denied"
                    if error.status in (401, 403)
                    else "transport_or_access",
                )
            )
        validation: Literal["reported_identity", "path_context_only"] = (
            "reported_identity"
            if dataset
            in (HistoryDataset.WEEKEND, HistoryDataset.LOOP, HistoryDataset.STAGES)
            and not data.empty
            else "path_context_only"
        )
        provenance = replace(self._metadata(path, provenance), validation=validation)
        return self._result(
            HistoryResult(
                HistoryStatus.EMPTY if data.empty else HistoryStatus.AVAILABLE,
                provenance,
                data,
            )
        )

    def _metadata(self, path: str, provenance: HistoryProvenance) -> HistoryProvenance:
        diagnostic = self.api.diagnostics().get(path, {})
        response_at = diagnostic.get("successful_response_at")
        http_status = diagnostic.get("http_status")
        return replace(
            provenance,
            delivery=str(diagnostic.get("delivery", "unknown")),
            response_at=response_at if isinstance(response_at, str) else None,
            http_status=http_status if isinstance(http_status, int) else None,
        )


class DemoHistoryProvider:
    """Small fictional values created in code; no fixtures or network fallback."""

    def clear(self) -> None:
        """The offline provider retains no data."""

    async def async_get_history(
        self, key: HistoricalRaceKey, dataset: HistoryDataset
    ) -> HistoryResult:
        # Empty examples are intentional; no NASCAR result is fabricated.
        payload: object
        if dataset == HistoryDataset.WEEKEND:
            payload = {
                "weekend_race": [
                    {
                        "race_id": key.race_id,
                        "series_id": key.series_id,
                        "race_season": key.season,
                        "race_name": "Fictional offline history demonstration",
                        "results": [
                            {
                                "driver_id": 99002,
                                "driver_fullname": "Fictional Demo Driver",
                                "car_number": "00",
                                "finishing_position": 1,
                                "laps_completed": 5,
                            }
                        ],
                    }
                ],
                "weekend_runs": [],
            }
        elif dataset == HistoryDataset.LAPS:
            payload = {"laps": [], "flags": []}
        elif dataset == HistoryDataset.NOTES:
            payload = {"laps": {}}
        else:
            payload = []
        data = PARSERS[dataset](payload, key)
        return HistoryResult(
            HistoryStatus.EMPTY if data.empty else HistoryStatus.AVAILABLE,
            HistoryProvenance(dataset, key, "fictional", "fictional", "offline"),
            data,
        )
