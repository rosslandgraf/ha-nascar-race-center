"""Independent asynchronous providers for slow driver and track metadata."""

from typing import Protocol

from .api import NascarApiClient
from .endpoints import DRIVERS, TRACKS
from .models import ProviderError
from .reference import (
    Driver,
    Track,
    demo_drivers,
    demo_tracks,
    parse_drivers,
    parse_tracks,
)

REFERENCE_TTL = 86400


class ReferenceProvider(Protocol):
    """Allow reference failure to be isolated from race and live providers."""

    async def async_get_drivers(self) -> tuple[Driver, ...]:
        """Return a directory without claiming it is a current entry list."""
        ...

    async def async_get_tracks(self) -> tuple[Track, ...]:
        """Return supported venue facts."""
        ...


class CFReferenceProvider:
    """Reuse authorized CF transport, its shared session/cache and backoff."""

    def __init__(self, api: NascarApiClient) -> None:
        """Take the same transport used by the schedule/live provider."""
        self.api = api
        self.driver_diagnostics: dict[str, object] = {}

    async def async_get_drivers(self) -> tuple[Driver, ...]:
        """Refresh driver metadata at most daily absent cache instructions."""
        self.driver_diagnostics = {"status": "not_parsed"}
        try:
            payload = await self.api.async_get_json(DRIVERS, minimum_ttl=REFERENCE_TTL)
        except ProviderError:
            self.driver_diagnostics["status"] = "request_failed"
            raise
        try:
            return parse_drivers(payload, diagnostics=self.driver_diagnostics)
        except ProviderError:
            self.driver_diagnostics["status"] = "invalid_schema_or_no_usable_ids"
            raise

    async def async_get_tracks(self) -> tuple[Track, ...]:
        """Keep venue lookup independent of the driver directory."""
        return parse_tracks(
            await self.api.async_get_json(TRACKS, minimum_ttl=REFERENCE_TTL)
        )


class DemoReferenceProvider:
    """Fictional in-memory metadata with no network dependencies."""

    async def async_get_drivers(self) -> tuple[Driver, ...]:
        """Return stable fictional NASCAR-like identities across all series."""
        return demo_drivers()

    async def async_get_tracks(self) -> tuple[Track, ...]:
        """Return the fictional schedule venue."""
        return demo_tracks()
