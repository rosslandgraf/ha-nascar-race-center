"""Optional feeds reuse shared HTTP cache/backoff without certifying freshness."""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest
from test_api import Response
from test_scoring import ACTIVE, NOW, fixture

from custom_components.nascar_race_center.api import NascarApiClient
from custom_components.nascar_race_center.endpoints import LIVE_POINTS
from custom_components.nascar_race_center.models import SchemaError
from custom_components.nascar_race_center.scoring import association_state
from custom_components.nascar_race_center.scoring_provider import CFScoringProvider


async def test_optional_cache_and_304_never_refresh_unknown_source_content_time():
    session = MagicMock()
    session.get.side_effect = [
        Response(
            body=json.dumps(fixture("points")).encode(), headers={"ETag": '"points-v1"'}
        ),
        Response(status=304),
    ]
    api = NascarApiClient(session)
    provider = CFScoringProvider(api)
    with patch("custom_components.nascar_race_center.api._monotonic", return_value=100):
        original = await provider.async_get_scoring("points")
        cached = await provider.async_get_scoring("points")
    assert session.get.call_count == 1
    with patch(
        "custom_components.nascar_race_center.api._monotonic", return_value=1100
    ):
        revalidated = await provider.async_get_scoring("points")
    assert session.get.call_count == 2
    assert session.get.call_args.kwargs["headers"]["If-None-Match"] == '"points-v1"'
    assert original == cached == revalidated
    assert original.provenance.endpoint == LIVE_POINTS
    assert revalidated.provenance.source_updated_at is None
    assert association_state(revalidated, ACTIVE, NOW) == "context_unknown"
    session.close.assert_not_called()


@pytest.mark.parametrize("kind", ["pits", "stages", "points"])
async def test_optional_schema_errors_are_provider_errors_without_raw_body(kind):
    session = MagicMock()
    session.get.return_value = Response(body=b'{"secret": "not-a-scoring-array"}')
    provider = CFScoringProvider(NascarApiClient(session))
    with pytest.raises(SchemaError, match="Invalid optional scoring feed") as error:
        await provider.async_get_scoring(kind)
    assert "secret" not in str(error.value)


async def test_provider_cancellation_is_not_an_optional_empty_dataset():
    api = MagicMock()
    from unittest.mock import AsyncMock

    api.async_get_json = AsyncMock(side_effect=asyncio.CancelledError)
    with pytest.raises(asyncio.CancelledError):
        await CFScoringProvider(api).async_get_scoring("points")
