"""Synthetic HTTP responses exercise transport without contacting NASCAR."""

import asyncio
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientConnectionError

from custom_components.nascar_race_center import api
from custom_components.nascar_race_center.api import NascarApiClient
from custom_components.nascar_race_center.endpoints import BASE_URL, LIVE_FEED
from custom_components.nascar_race_center.models import (
    AccessDeniedError,
    ProviderError,
    RateLimitedError,
    SchemaError,
)

SCHEDULE = "/cacher/2026/race_list_basic.json"


class Response:
    """Minimal streaming HTTP response used by a caller-owned fake session."""

    def __init__(self, status=200, body=b'{"series_1":[]}', headers=None):
        self.status = status
        self.headers = headers or {}
        self.content = self
        self.body = body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def iter_chunked(self, size):
        for offset in range(0, len(self.body), size):
            yield self.body[offset : offset + size]


def client_with(*responses):
    session = MagicMock()
    session.get.side_effect = responses
    return NascarApiClient(session), session


async def test_cache_deduplicates_concurrent_requests():
    client, session = client_with(Response())
    result = await asyncio.gather(
        client.async_get_json(SCHEDULE, minimum_ttl=3600),
        client.async_get_json(SCHEDULE, minimum_ttl=3600),
    )
    assert result == [{"series_1": []}, {"series_1": []}]
    session.get.assert_called_once()
    assert session.get.call_args.args == (f"{BASE_URL}{SCHEDULE}",)
    assert session.get.call_args.kwargs["allow_redirects"] is False
    assert session.get.call_args.kwargs["timeout"].total == 15
    session.close.assert_not_called()


async def test_conditional_get_refreshes_validators_without_losing_no_cache():
    client, session = client_with(
        Response(headers={"Cache-Control": "no-cache", "ETag": '"first"'}),
        Response(304, headers={"ETag": '"second"'}),
        Response(304),
    )
    for _ in range(3):
        assert await client.async_get_json(SCHEDULE, minimum_ttl=3600) == {
            "series_1": []
        }
    assert session.get.call_count == 3
    assert session.get.call_args_list[1].kwargs["headers"]["If-None-Match"] == '"first"'
    assert (
        session.get.call_args_list[2].kwargs["headers"]["If-None-Match"] == '"second"'
    )


async def test_last_modified_and_age_expiry(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    modified = "Tue, 20 Oct 2026 12:00:00 GMT"
    client, session = client_with(
        Response(
            headers={
                "Cache-Control": "max-age=120",
                "Age": "100",
                "Last-Modified": modified,
            }
        ),
        Response(304, headers={"Cache-Control": "max-age=300", "Age": "0"}),
    )
    await client.async_get_json(SCHEDULE)
    clock[0] += 19
    await client.async_get_json(SCHEDULE)
    assert session.get.call_count == 1
    clock[0] += 2
    await client.async_get_json(SCHEDULE)
    assert session.get.call_count == 2
    assert session.get.call_args.kwargs["headers"]["If-Modified-Since"] == modified


async def test_no_store_never_retains_body_or_validators():
    client, session = client_with(
        Response(headers={"Cache-Control": "no-store", "ETag": '"secret"'}),
        Response(),
    )
    await client.async_get_json(SCHEDULE, minimum_ttl=3600)
    await client.async_get_json(SCHEDULE, minimum_ttl=3600)
    assert session.get.call_count == 2
    assert "If-None-Match" not in session.get.call_args.kwargs["headers"]


@pytest.mark.parametrize("status", [401, 403])
async def test_denied_does_not_request_credentials_or_echo_body(status):
    client, session = client_with(Response(status, b"sensitive response"))
    with pytest.raises(AccessDeniedError) as error:
        await client.async_get_json(SCHEDULE)
    assert error.value.status == status
    assert "sensitive" not in str(error.value)
    assert session.get.call_count == 1


@pytest.mark.parametrize("status", [302, 404])
async def test_unexpected_status_is_explicit_without_following_redirects(status):
    client, session = client_with(Response(status))
    with pytest.raises(ProviderError) as error:
        await client.async_get_json(SCHEDULE)
    assert error.value.status == status
    assert session.get.call_count == 1


async def test_rate_limit_stops_all_endpoints_without_retry_loop(monkeypatch):
    monkeypatch.setattr(api, "_monotonic", lambda: 1000)
    client, session = client_with(Response(429, headers={"Retry-After": "600"}))
    with pytest.raises(RateLimitedError) as error:
        await client.async_get_json(SCHEDULE)
    assert error.value.retry_after == 600
    with pytest.raises(RateLimitedError):
        await client.async_get_json(LIVE_FEED)
    assert session.get.call_count == 1


async def test_http_date_retry_hint():
    retry_at = datetime.now(UTC) + timedelta(hours=1)
    client, _ = client_with(
        Response(429, headers={"Retry-After": format_datetime(retry_at)})
    )
    with pytest.raises(RateLimitedError) as error:
        await client.async_get_json(SCHEDULE)
    assert 3590 < error.value.retry_after <= 3600


async def test_pathological_retry_hint_cannot_overflow_coordinator_timedelta():
    client, _ = client_with(Response(429, headers={"Retry-After": "1e300"}))
    with pytest.raises(RateLimitedError) as error:
        await client.async_get_json(SCHEDULE)
    assert timedelta(seconds=error.value.retry_after) == timedelta(days=366)


async def test_optional_live_failure_does_not_cool_down_schedule(monkeypatch):
    monkeypatch.setattr(api, "_monotonic", lambda: 1000)
    client, session = client_with(Response(503), Response())
    with pytest.raises(ProviderError) as error:
        await client.async_get_json(LIVE_FEED)
    assert error.value.retry_after >= 60
    assert await client.async_get_json(SCHEDULE) == {"series_1": []}
    with pytest.raises(ProviderError):
        await client.async_get_json(LIVE_FEED)
    assert session.get.call_count == 2


async def test_backoff_grows_and_resets_after_success(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    monkeypatch.setattr(api.random, "uniform", lambda *_: 0)
    client, session = client_with(
        Response(503), Response(503), Response(), Response(503)
    )
    for delay in (60, 120):
        with pytest.raises(ProviderError) as error:
            await client.async_get_json(SCHEDULE)
        assert error.value.retry_after == delay
        clock[0] += delay + 1
    await client.async_get_json(SCHEDULE)
    with pytest.raises(ProviderError) as error:
        await client.async_get_json(SCHEDULE)
    assert error.value.retry_after == 60
    assert session.get.call_count == 4


@pytest.mark.parametrize("failure", [TimeoutError(), ClientConnectionError()])
async def test_network_errors_normalize_and_back_off(failure):
    client, session = client_with(failure)
    with pytest.raises(ProviderError) as error:
        await client.async_get_json(SCHEDULE)
    assert error.value.status is None
    assert error.value.retry_after >= 60
    with pytest.raises(ProviderError):
        await client.async_get_json(SCHEDULE)
    assert session.get.call_count == 1


async def test_cancellation_propagates_and_releases_request_lock():
    client, session = client_with(asyncio.CancelledError(), Response())
    with pytest.raises(asyncio.CancelledError):
        await client.async_get_json(SCHEDULE)
    assert await client.async_get_json(SCHEDULE) == {"series_1": []}
    assert session.get.call_count == 2


@pytest.mark.parametrize("body", [b"", b"<html>Login</html>", b"{", b"\xff"])
async def test_malformed_or_empty_json_is_not_a_schedule(body):
    client, _ = client_with(Response(body=body))
    with pytest.raises(SchemaError):
        await client.async_get_json(SCHEDULE)


@pytest.mark.parametrize(
    "body",
    [
        b'{"series_id":1,"series_id":2,"race_id":99001}',
        b'{"vehicles":[{"driver":{"driver_id":99001,"driver_id":99002}}]}',
    ],
)
async def test_duplicate_source_keys_cannot_silently_replace_reported_identity(body):
    """Conflicting series or driver identities must not route to the last key."""
    client, _ = client_with(Response(body=body))
    with pytest.raises(SchemaError, match="valid JSON"):
        await client.async_get_json(SCHEDULE)


async def test_response_size_is_bounded():
    client, _ = client_with(Response(body=b" " * (2 * 1024 * 1024 + 1)))
    with pytest.raises(SchemaError, match="size limit"):
        await client.async_get_json(SCHEDULE)


async def test_cache_has_a_bounded_number_of_seasons():
    client, session = client_with(*(Response() for _ in range(8)))
    for year in range(2020, 2027):
        await client.async_get_json(
            f"/cacher/{year}/race_list_basic.json", minimum_ttl=3600
        )
    await client.async_get_json("/cacher/2020/race_list_basic.json", minimum_ttl=3600)
    assert session.get.call_count == 8


@pytest.mark.parametrize(
    "path",
    ["https://feed.nascar.com/", "https://evil.invalid/", "/drive/1/configs-ng.json"],
)
async def test_non_catalog_endpoint_is_rejected_before_io(path):
    client, session = client_with()
    with pytest.raises(ValueError, match="catalog"):
        await client.async_get_json(path)
    session.get.assert_not_called()


@pytest.mark.parametrize("hint", ["nan", "inf", "-1", "garbage"])
async def test_malformed_retry_hint_uses_finite_backoff(hint):
    client, _ = client_with(Response(503, headers={"Retry-After": hint}))
    with pytest.raises(ProviderError) as error:
        await client.async_get_json(SCHEDULE)
    assert 60 <= error.value.retry_after <= 66


@pytest.mark.parametrize("header", ["max-age=nan", "max-age=inf", "max-age=invalid"])
async def test_malformed_cache_lifetime_never_persists_forever(header):
    client, session = client_with(
        Response(headers={"Cache-Control": header}), Response()
    )
    await client.async_get_json(SCHEDULE)
    await client.async_get_json(SCHEDULE)
    assert session.get.call_count == 2
