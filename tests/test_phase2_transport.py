"""Phase 2 endpoints reuse cache validators, bounded memory and backoff."""

from unittest.mock import MagicMock, patch

import pytest
from test_api import Response

from custom_components.nascar_race_center.api import NascarApiClient
from custom_components.nascar_race_center.endpoints import (
    DRIVERS,
    LIVE_FEED,
    TRACKS,
    schedule_feed_path,
    schedule_path,
)
from custom_components.nascar_race_center.models import ProviderError


async def test_all_phase2_feeds_retain_validators_for_both_seasons() -> None:
    """Six session feeds, two season lists, references and live coexist."""
    paths = [
        *(schedule_path(year) for year in (2026, 2027)),
        *(
            schedule_feed_path(year, series)
            for year in (2026, 2027)
            for series in (1, 2, 3)
        ),
        DRIVERS,
        TRACKS,
        LIVE_FEED,
    ]
    session = MagicMock()
    session.get.side_effect = [
        *(Response(headers={"ETag": '"v1"'}) for _ in paths),
        *(Response(status=304) for _ in paths),
    ]
    client = NascarApiClient(session, max_cache_entries=16)
    with patch("custom_components.nascar_race_center.api._monotonic", return_value=100):
        for path in paths:
            await client.async_get_json(path, minimum_ttl=3600)
            await client.async_get_json(path, minimum_ttl=3600)
    assert session.get.call_count == len(paths)
    with patch(
        "custom_components.nascar_race_center.api._monotonic", return_value=4000
    ):
        for path in paths:
            await client.async_get_json(path, minimum_ttl=3600)
    for request in session.get.call_args_list[len(paths) :]:
        assert request.kwargs["headers"]["If-None-Match"] == '"v1"'


async def test_reference_503_cooldown_does_not_block_schedules() -> None:
    """Per-endpoint transient backoff cannot take down unrelated races."""
    session = MagicMock()
    session.get.side_effect = [Response(status=503), Response()]
    client = NascarApiClient(session, max_cache_entries=16)
    with pytest.raises(ProviderError):
        await client.async_get_json(DRIVERS)
    with pytest.raises(ProviderError, match="cooldown"):
        await client.async_get_json(DRIVERS)
    assert await client.async_get_json(schedule_path(2026)) == {"series_1": []}
    assert session.get.call_count == 2


@pytest.mark.parametrize("status", [401, 403, 404])
async def test_missing_shared_season_feed_is_not_requested_once_per_series(
    status: int,
) -> None:
    """Unavailable global schedules are negatively cached across series calls."""
    session = MagicMock()
    session.get.side_effect = [Response(status=status), Response()]
    client = NascarApiClient(session, max_cache_entries=16)
    for _ in (1, 2, 3):
        with pytest.raises(ProviderError) as error:
            await client.async_get_json(schedule_path(2027))
        assert error.value.status == status
    assert await client.async_get_json(TRACKS) == {"series_1": []}
    assert session.get.call_count == 2


@pytest.mark.parametrize(
    "path",
    [
        "/cacher/2026/4/schedule-feed.json",
        "/cacher/2026/1/../../drivers.json",
        "/cacher/drivers.json?token=test",
        "/cacher/tracks.json/",
    ],
)
async def test_new_catalog_remains_exact(path: str) -> None:
    """Adding reference feeds must not broaden arbitrary provider access."""
    session = MagicMock()
    client = NascarApiClient(session)
    with pytest.raises(ValueError, match="approved catalog"):
        await client.async_get_json(path)
    session.get.assert_not_called()
