"""Read-only projections for sensors and later race-center consumers."""

from dataclasses import dataclass
from typing import Literal

from homeassistant.util import dt as dt_util

from .models import LiveSnapshot
from .polling import active_kind
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

    Current scoring and active/completed progress require established source
    freshness. A checkered observation denotes
    session completion only, not official classification or finalized results.
    Failed/stale/unknown-freshness sources retain diagnostic context only.
    """

    snapshot: LiveSnapshot | None
    health: FeedHealth
    observation_state: str | None = None

    @property
    def available(self) -> bool:
        """Only a successful, matching source with known freshness supplies scoring."""
        snapshot = self.snapshot
        return (
            self.health == "ok"
            and snapshot is not None
            and snapshot.run_id is not None
            and snapshot.status in {"race", "practice", "qualifying"}
            and snapshot.flag != "cold_track"
            and not (
                snapshot.leaderboard is not None and not snapshot.leaderboard.drivers
            )
            and self.observation_state not in {"timestamp_only", "clock_unchanged"}
        )

    @property
    def session_status(self) -> str | None:
        """Do not infer activity from run_type, last HTTP time or lap progress."""
        if self.health in {"not_reported", "no_active_session", "stale"}:
            return self.health
        if self.health != "ok" or self.snapshot is None:
            return None
        if (
            self.snapshot.leaderboard is not None
            and not self.snapshot.leaderboard.drivers
        ):
            return "no_active_session"
        if self.snapshot.run_id is None or self.snapshot.status is None:
            return (
                "observations_unavailable"
                if self.observation_state is not None
                else None
            )
        if self.snapshot.flag == "checkered":
            return "completed"
        if self.snapshot.flag == "cold_track" or self.observation_state in {
            "timestamp_only",
            "clock_unchanged",
        }:
            return "latest_recorded"
        if self.observation_state is not None and self.snapshot.leaderboard is None:
            return "observations_unavailable"
        if self.observation_state is not None and self.snapshot.flag_state_code not in {
            None,
            0,
            1,
            2,
            3,
            4,
            5,
            8,
            9,
        }:
            return "activity_unconfirmed"
        if active_kind(self.snapshot, dt_util.utcnow()):
            return (
                "activity_unconfirmed"
                if self.observation_state == "first_observation"
                else "active"
            )
        return "activity_unconfirmed" if self.observation_state is not None else None

    @property
    def leaderboard(self) -> Leaderboard | None:
        """Return an immutable current reported field, never a saved prior race."""
        return self.snapshot.leaderboard if self.available and self.snapshot else None

    @property
    def leaderboard_unavailable_reason(self) -> str | None:
        """Explain withholding without confusing transport with reported activity."""
        if self.health != "ok":
            return self.health
        snapshot = self.snapshot
        if snapshot is None:
            return "no_active_session"
        if snapshot.run_id is None:
            return "missing_run_identity"
        if snapshot.status is None:
            return "unsupported_run_type"
        if snapshot.flag == "cold_track":
            return "cold_track"
        if snapshot.leaderboard_failed:
            return "vehicle_schema_rejected"
        if snapshot.leaderboard is None:
            return "vehicles_not_reported"
        if not snapshot.leaderboard.drivers:
            return "no_reported_vehicles"
        if self.observation_state in {"timestamp_only", "clock_unchanged"}:
            return self.observation_state
        return None

    def driver(self, driver_id: int) -> LiveDriver | None:
        """Look up a favorite without reference-feed or car/name dependencies."""
        board = self.leaderboard
        return board.by_driver.get(driver_id) if board is not None else None
