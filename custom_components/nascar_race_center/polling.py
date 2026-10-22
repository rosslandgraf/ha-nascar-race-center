"""Pure polling decisions over normalized evidence, separate from data/event meaning."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from .const import LIVE_STALE_AFTER
from .models import LiveSnapshot, Race


@dataclass(frozen=True, slots=True)
class PollingLimits:
    """Reviewed provider constraints, never supplied by configuration acknowledgements.

    Changing CF's record requires independently verified permitted limits and a
    reviewed adapter change. This object is an engineering boundary, not a grant.
    """

    name: str
    minimum_seconds: int = 300
    adaptive: bool = False

    @property
    def fast_permitted(self) -> bool:
        return self.adaptive and self.minimum_seconds < 300


CF_LIMITS = PollingLimits("cf_unverified_cadence")
CONSERVATIVE_LIMITS = PollingLimits("unknown_provider")
OFFLINE_LIMITS = PollingLimits("offline_synthetic", 10, True)


@dataclass(frozen=True, slots=True)
class PollDecision:
    seconds: float
    reason: str


def active_kind(snapshot: LiveSnapshot | None, now: datetime) -> str | None:
    """Fresh complete run identity and supported activity, never schedule passage."""
    if (
        snapshot is None
        or snapshot.race_id <= 0
        or snapshot.run_id is None
        or snapshot.run_id <= 0
        or snapshot.source_updated_at is None
        or not timedelta(0) <= now - snapshot.source_updated_at <= LIVE_STALE_AFTER
        or snapshot.flag in {"checkered", "cold_track"}
    ):
        return None
    if snapshot.status == "race":
        if snapshot.flag in {"green", "yellow", "red", "white"} and (
            snapshot.lap is not None and snapshot.lap > 0
        ):
            return "race"
    elif snapshot.status in {"practice", "qualifying"}:
        if snapshot.leaderboard is not None and not snapshot.leaderboard_failed:
            if any(row.is_on_track is True for row in snapshot.leaderboard.drivers):
                return snapshot.status
    return None


def legacy_decision(
    snapshot: LiveSnapshot | None,
    races: tuple[Race, ...],
    now: datetime,
    minimum: int,
) -> PollDecision:
    """Keep CF's conservative budget; on-track non-race runs need no race lap."""
    if (kind := active_kind(snapshot, now)) in {"practice", "qualifying"}:
        return PollDecision(minimum, f"legacy_active_{kind}")
    if (
        snapshot is not None
        and snapshot.source_updated_at is not None
        and -timedelta(minutes=5)
        <= now - snapshot.source_updated_at
        <= LIVE_STALE_AFTER
        and snapshot.flag in {"green", "yellow", "red", "white"}
        and snapshot.lap is not None
        and snapshot.lap > 0
    ):
        return PollDecision(minimum, "legacy_active")
    seconds, reason = max(minimum, 21600), "off_season"
    for race in races:
        if race.start_time is None:
            continue
        delta = race.start_time - now
        if -timedelta(hours=8) <= delta <= timedelta(hours=2):
            seconds, reason = min(seconds, max(minimum, 900)), "legacy_race_window"
        elif timedelta(0) <= delta <= timedelta(days=2) and seconds > 3600:
            seconds, reason = min(seconds, max(minimum, 3600)), "idle"
    return PollDecision(seconds, reason)


def adaptive_decision(
    snapshot: LiveSnapshot | None,
    races: tuple[Race, ...],
    now: datetime,
    *,
    schedules_known: bool,
    approaching_seconds: int = 60,
) -> PollDecision:
    """Choose the nearest evidence-backed opportunity across selected series.

    A scheduled window only drives discovery, never claims an active session.
    Unknown duration gets a bounded 30-minute discovery window, not an invented
    session end. Overnight is a gap longer than six hours to the next known start.
    """
    if kind := active_kind(snapshot, now):
        return PollDecision(10, f"active_{kind}")
    candidates: list[PollDecision] = []
    unknown = not schedules_known
    future_boundaries: list[datetime] = []
    for race in races:
        if race.status in {"canceled", "cancelled", "completed"}:
            continue
        sessions = [
            session
            for session in race.sessions
            if session.kind in {"race", "practice", "qualifying"}
            and session.status not in {"canceled", "cancelled", "completed"}
        ]
        windows = [(session.start_time, session.end_time) for session in sessions]
        if not any(session.kind == "race" for session in sessions):
            windows.append((race.start_time, None))
        known = [(start, end) for start, end in windows if start is not None]
        unknown |= len(known) < len(windows) or race.sessions_failed
        future = [start for start, _ in known if start > now]
        future_boundaries.extend(start - timedelta(minutes=30) for start in future)
        for start, end in known:
            delta = (start - now).total_seconds()
            # Continued scheduled discovery is bounded, even with a very long
            # published duration; actual activity requires the live evidence.
            discovery_end = (
                min(end, start + timedelta(hours=8))
                if end
                else (start + timedelta(minutes=30))
            )
            if 0 < delta <= 1800:
                candidates.append(
                    PollDecision(approaching_seconds, "approaching_session")
                )
            elif start <= now < discovery_end:
                candidates.append(PollDecision(300, "scheduled_window"))
            elif end is None and start <= now < start + timedelta(hours=8):
                candidates.append(PollDecision(3600, "conservative_fallback"))
        if known and future:
            first = min(start for start, _ in known)
            if first <= now and min(future) - now <= timedelta(hours=6):
                candidates.append(PollDecision(300, "between_sessions"))
        if any(0 < (start - now).total_seconds() <= 7 * 86400 for start in future):
            candidates.append(PollDecision(3600, "idle"))
    if unknown:
        candidates.append(PollDecision(3600, "conservative_fallback"))
    decision = (
        min(candidates, key=lambda item: item.seconds)
        if candidates
        else (PollDecision(21600, "off_season"))
    )
    # Wake the existing coordinator at the approach boundary, without another
    # polling timer or requiring the six-hour schedule refresh to notice it.
    until_boundary = min(
        (
            (deadline - now).total_seconds()
            for deadline in future_boundaries
            if deadline > now
        ),
        default=decision.seconds,
    )
    return PollDecision(max(10, min(decision.seconds, until_boundary)), decision.reason)
