"""Read-only projections for sensors and later race-center consumers."""

from dataclasses import dataclass
from typing import Literal

from .models import LiveSnapshot
from .timing import Leaderboard, LiveDriver

type FeedHealth = Literal[
    "denied",
    "offline",
    "not_reported",
    "no_active_session",
    "freshness_unknown",
    "stale",
    "ok",
]


@dataclass(frozen=True, slots=True)
class LiveView:
    """Separate reported facts, transport health and evidence-limited progress.

    A matching source with unknown freshness may expose reported values, but
    cannot establish active/completed progress. A checkered observation denotes
    session completion only, not official classification or finalized results.
    Failed/stale sources retain context for diagnostics, never current scoring.
    """

    snapshot: LiveSnapshot | None
    health: FeedHealth

    @property
    def available(self) -> bool:
        """Only a successfully read, matching, non-stale source supplies facts."""
        return self.health in {"ok", "freshness_unknown"}

    @property
    def session_status(self) -> str | None:
        """Do not infer activity from run_type, last HTTP time or lap progress."""
        if self.health in {"not_reported", "no_active_session", "stale"}:
            return self.health
        if self.health != "ok" or self.snapshot is None:
            return None
        if self.snapshot.flag == "checkered":
            return "completed"
        if (
            self.snapshot.flag in {"green", "yellow", "red", "white"}
            and self.snapshot.lap is not None
            and self.snapshot.lap > 0
        ):
            return "active"
        return None

    @property
    def leaderboard(self) -> Leaderboard | None:
        """Return an immutable current reported field, never a saved prior race."""
        return self.snapshot.leaderboard if self.available and self.snapshot else None

    def driver(self, driver_id: int) -> LiveDriver | None:
        """Look up a favorite without reference-feed or car/name dependencies."""
        board = self.leaderboard
        return board.by_driver.get(driver_id) if board is not None else None
