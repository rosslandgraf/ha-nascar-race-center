"""A reported lap-averages 403 cannot erase valid peer datasets or spin retries."""

import json

import pytest
from test_api import Response, client_with
from test_history import contextualize, fixture

from custom_components.nascar_race_center.endpoints import historical_path
from custom_components.nascar_race_center.history import HistoryService
from custom_components.nascar_race_center.history_models import HistoricalRaceKey
from custom_components.nascar_race_center.history_models import HistoryDataset as Kind
from custom_components.nascar_race_center.history_models import HistoryStatus as Status
from custom_components.nascar_race_center.history_provider import CFHistoryProvider


@pytest.mark.parametrize("series", [1, 2, 3])
async def test_lap_average_denial_is_partial_and_repeated_selection_obeys_cooldown(
    series,
):
    key = HistoricalRaceKey(2026, series, 5605)
    weekend = contextualize(fixture(Kind.WEEKEND), key)
    client, session = client_with(
        Response(body=json.dumps(weekend).encode()), Response(403)
    )
    provider = CFHistoryProvider(client)
    service = HistoryService(provider, (1, 2, 3))
    result = await service.async_get(key, (Kind.WEEKEND, Kind.AVERAGES))
    assert result.status == Status.PARTIAL
    assert result.dataset(Kind.WEEKEND).status == Status.AVAILABLE
    denied = result.dataset(Kind.AVERAGES)
    assert denied.status == Status.NETWORK_ERROR
    assert denied.provenance.http_status == 403
    assert denied.reason == "access_denied"
    assert (
        historical_path(key, Kind.AVERAGES)
        == f"/cacher/2026/{series}/5605/lap-averages.json"
    )
    assert session.get.call_count == 2
    for _ in range(5):
        again = await service.async_get(key, (Kind.WEEKEND, Kind.AVERAGES))
        assert again.status == Status.PARTIAL
    assert session.get.call_count == 2
    summaries = list(provider.dataset_diagnostics.values())
    assert len(summaries) == 2
    assert (
        next(s for s in summaries if s["dataset"] == "averages")["http_status"] == 403
    )
    assert "results" not in repr(summaries)
    await service.async_close()
    assert not provider.dataset_diagnostics
