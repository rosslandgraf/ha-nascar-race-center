"""Optional global feeds share transport but never inherit leaderboard context."""

from typing import Literal, Protocol

from .api import NascarApiClient
from .endpoints import LIVE_PITS, LIVE_POINTS, LIVE_STAGES
from .models import SchemaError
from .scoring import (
    Provenance,
    ScoringFeed,
    parse_pit_feed,
    parse_points_feed,
    parse_stage_feed,
)

type ScoringKind = Literal["pits", "stages", "points"]
SCORING_KINDS: tuple[ScoringKind, ...] = ("pits", "stages", "points")


class ScoringProvider(Protocol):
    async def async_get_scoring(self, kind: ScoringKind) -> ScoringFeed | None:
        """Return one independent reported dataset, without live association."""
        ...


class CFScoringProvider:
    def __init__(self, api: NascarApiClient) -> None:
        self.api = api

    async def async_get_scoring(self, kind: ScoringKind) -> ScoringFeed | None:
        """No source clock exists in these observed shapes; receipt is not one."""
        path, parser = {
            "pits": (LIVE_PITS, parse_pit_feed),
            "stages": (LIVE_STAGES, parse_stage_feed),
            "points": (LIVE_POINTS, parse_points_feed),
        }[kind]
        payload = await self.api.async_get_json(path, minimum_ttl=900)
        try:
            return parser(payload, Provenance(path))
        except ValueError as err:
            raise SchemaError("Invalid optional scoring feed") from err


class DemoScoringProvider:
    async def async_get_scoring(self, kind: ScoringKind) -> ScoringFeed | None:
        """An empty offline live feed accompanies fictional demo schedules."""
        return None
