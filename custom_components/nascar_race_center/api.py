"""Bounded anonymous HTTP transport with conditional caching and backoff."""

import asyncio
import json
import math
import random
import re
import time
from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from aiohttp import ClientError, ClientSession, ClientTimeout

from .endpoints import BASE_URL, DRIVERS, LIVE_FEED, TRACKS
from .models import AccessDeniedError, ProviderError, RateLimitedError, SchemaError

_MAX_RESPONSE_BYTES = 2 * 1024 * 1024
_MAX_CACHE_ENTRIES = 6
# Malformed-but-finite Retry-After values must not overflow HA timedeltas.
_MAX_RETRY_AFTER = 366 * 86400
_SCHEDULE_PATH = re.compile(r"/cacher/[0-9]{4}/race_list_basic\.json")
_SESSION_PATH = re.compile(r"/cacher/[0-9]{4}/[123]/schedule-feed\.json")
_monotonic = time.monotonic


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous keys before they can overwrite series/driver identity."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


@dataclass(slots=True)
class _CacheEntry:
    payload: object
    expires_at: float
    etag: str | None
    last_modified: str | None
    cache_headers: dict[str, str]


def _http_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        result = parsedate_to_datetime(value)
        if result.tzinfo is None:
            result = result.replace(tzinfo=UTC)
        return result.astimezone(UTC)
    except TypeError, ValueError, OverflowError:
        return None


def _retry_after(value: str | None) -> float:
    """Interpret server seconds or HTTP dates without trusting malformed hints."""
    if value is None:
        return 0
    try:
        seconds = float(value)
        if math.isfinite(seconds) and seconds >= 0:
            return min(seconds, _MAX_RETRY_AFTER)
    except ValueError:
        pass
    retry_at = _http_date(value)
    if retry_at is None:
        return 0
    return min(_MAX_RETRY_AFTER, max(0, (retry_at - datetime.now(UTC)).total_seconds()))


def _cache_policy(headers: Mapping[str, str], minimum_ttl: float) -> tuple[bool, float]:
    """Honor validators/no-store/no-cache, max-age, Age and Expires headers."""
    directives = {
        part.strip().lower().split("=", 1)[0]: part.strip().split("=", 1)[-1]
        for part in headers.get("Cache-Control", "").split(",")
        if part.strip()
    }
    if "no-store" in directives:
        return False, 0
    if "no-cache" in directives:
        return True, 0
    lifetime = max(0, minimum_ttl)
    if "max-age" in directives:
        try:
            lifetime = float(directives["max-age"].strip('"'))
            lifetime = max(0, lifetime) if math.isfinite(lifetime) else 0
        except ValueError:
            lifetime = 0
    elif expires := _http_date(headers.get("Expires")):
        lifetime = max(0, (expires - datetime.now(UTC)).total_seconds())
    try:
        age = float(headers.get("Age", "0"))
        age = max(0, age) if math.isfinite(age) else 0
    except ValueError:
        age = 0
    # An unreasonable upstream lifetime must not keep in-memory data forever.
    return True, max(0, min(lifetime - age, 86400))


class NascarApiClient:
    """Use the managed session without introducing authentication or retries.

    A failed call raises immediately. Future calls observe monotonic cooldowns
    scoped to the endpoint, except host-wide 429 limits. Coordinators decide
    when to retry and retain their last good data. Server retry hints are bounded
    to one leap year to keep downstream datetime arithmetic representable.
    """

    def __init__(
        self, session: ClientSession, *, max_cache_entries: int = _MAX_CACHE_ENTRIES
    ) -> None:
        """Retain the caller-owned session; never close it on unload."""
        self._session = session
        if not 1 <= max_cache_entries <= 24:
            raise ValueError("Cache size must be between 1 and 24 endpoints")
        self._max_cache_entries = max_cache_entries
        self._cache: OrderedDict[str, _CacheEntry] = OrderedDict()
        self._request_lock = asyncio.Lock()
        self._retry_at = 0.0
        self._failures: OrderedDict[str, int] = OrderedDict()
        self._cooldowns: OrderedDict[str, tuple[float, int | None]] = OrderedDict()

    def _failure(
        self, path: str, message: str, status: int | None, hint: float = 0
    ) -> ProviderError:
        failures = self._failures.get(path, 0) + 1
        self._failures[path] = failures
        self._failures.move_to_end(path)
        while len(self._failures) > 24:
            self._failures.popitem(last=False)
        backoff = min(3600, 60 * 2 ** min(failures - 1, 6))
        delay = max(hint, backoff + random.uniform(0, backoff * 0.1))
        if status == 429:
            self._retry_at = _monotonic() + delay
        else:
            self._cooldowns[path] = (_monotonic() + delay, status)
            self._cooldowns.move_to_end(path)
            while len(self._cooldowns) > 24:
                self._cooldowns.popitem(last=False)
        error = RateLimitedError if status == 429 else ProviderError
        return error(message, retry_after=delay, status=status)

    async def async_get_json(self, path: str, *, minimum_ttl: float = 0) -> object:
        """Fetch an allowlisted CF JSON document, with one in-flight request."""
        if (
            path not in {LIVE_FEED, DRIVERS, TRACKS}
            and _SCHEDULE_PATH.fullmatch(path) is None
            and _SESSION_PATH.fullmatch(path) is None
        ):
            raise ValueError("Endpoint is not in the approved catalog")
        async with self._request_lock:
            cached = self._cache.get(path)
            if cached is not None and cached.expires_at > _monotonic():
                self._cache.move_to_end(path)
                return cached.payload
            retry_at, status = self._cooldowns.get(path, (0.0, None))
            if self._retry_at >= retry_at:
                retry_at, status = self._retry_at, 429
            remaining = retry_at - _monotonic()
            if remaining > 0:
                cooldown_error = (
                    RateLimitedError
                    if status == 429
                    else AccessDeniedError
                    if status in {401, 403}
                    else ProviderError
                )
                raise cooldown_error(
                    "Provider cooldown is active",
                    retry_after=remaining,
                    status=status,
                )
            headers = {"Accept": "application/json"}
            if cached is not None:
                if cached.etag is not None:
                    headers["If-None-Match"] = cached.etag
                if cached.last_modified is not None:
                    headers["If-Modified-Since"] = cached.last_modified
            try:
                async with self._session.get(
                    f"{BASE_URL}{path}",
                    headers=headers,
                    timeout=ClientTimeout(total=15),
                    allow_redirects=False,
                ) as response:
                    if response.status == 304:
                        if cached is None:
                            raise SchemaError("Received 304 without a cached response")
                        cache_headers = dict(cached.cache_headers)
                        for name in ("Cache-Control", "Expires", "Age"):
                            if name in response.headers:
                                cache_headers[name] = response.headers[name]
                        store, ttl = _cache_policy(cache_headers, minimum_ttl)
                        cached.expires_at = _monotonic() + ttl
                        cached.cache_headers = cache_headers
                        cached.etag = response.headers.get("ETag", cached.etag)
                        cached.last_modified = response.headers.get(
                            "Last-Modified", cached.last_modified
                        )
                        if not store:
                            del self._cache[path]
                        self._failures.pop(path, None)
                        self._cooldowns.pop(path, None)
                        return cached.payload
                    if response.status in (401, 403):
                        error = self._failure(
                            path,
                            "Anonymous CF endpoint access was denied",
                            response.status,
                        )
                        raise AccessDeniedError(
                            "Anonymous CF endpoint access was denied",
                            status=response.status,
                            retry_after=error.retry_after,
                        )
                    if response.status == 429 or response.status >= 500:
                        raise self._failure(
                            path,
                            "CF endpoint is temporarily unavailable",
                            response.status,
                            _retry_after(response.headers.get("Retry-After")),
                        )
                    if response.status != 200:
                        raise self._failure(
                            path,
                            "CF endpoint returned an unexpected HTTP status",
                            response.status,
                        )
                    body = bytearray()
                    async for chunk in response.content.iter_chunked(65536):
                        body.extend(chunk)
                        if len(body) > _MAX_RESPONSE_BYTES:
                            raise SchemaError("CF response exceeded the size limit")
                    try:
                        payload: object = json.loads(
                            body, object_pairs_hook=_unique_object
                        )
                    except (ValueError, UnicodeDecodeError) as err:
                        raise SchemaError(
                            "CF endpoint did not return valid JSON"
                        ) from err
                    store, ttl = _cache_policy(response.headers, minimum_ttl)
                    if store:
                        self._cache[path] = _CacheEntry(
                            payload,
                            _monotonic() + ttl,
                            response.headers.get("ETag"),
                            response.headers.get("Last-Modified"),
                            {
                                name: response.headers[name]
                                for name in ("Cache-Control", "Expires", "Age")
                                if name in response.headers
                            },
                        )
                        self._cache.move_to_end(path)
                        while len(self._cache) > self._max_cache_entries:
                            self._cache.popitem(last=False)
                    else:
                        self._cache.pop(path, None)
                    self._failures.pop(path, None)
                    self._cooldowns.pop(path, None)
                    return payload
            except (ClientError, TimeoutError) as err:
                raise self._failure(
                    path, "Unable to reach the CF endpoint", None
                ) from err
