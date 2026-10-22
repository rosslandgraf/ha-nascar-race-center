"""Immutable normalized models and conservative CF parsing.

Field provenance is recorded in docs/SCHEMA_EVIDENCE.md. Optional fields can
vanish without inventing values; invalid identities/envelopes fail explicitly.
"""

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from hashlib import sha256

from .scoring import CurrentStage, parse_current_stage
from .timing import Leaderboard, parse_leaderboard


class ProviderError(Exception):
    """An upstream failure safe to expose without raw response/credential data."""

    def __init__(
        self,
        message: str,
        *,
        retry_after: float | None = None,
        status: int | None = None,
    ) -> None:
        """Retain only normalized failure metadata."""
        super().__init__(message)
        self.retry_after = retry_after
        self.status = status


class SchemaError(ProviderError):
    """The response cannot safely be interpreted."""


class AccessDeniedError(ProviderError):
    """The anonymous endpoint denied access; do not request credentials."""


class RateLimitedError(ProviderError):
    """The provider requested a pause before another request."""


class PollingDeferred(ProviderError):
    """A persisted request slot has not expired; no network failure occurred."""


@dataclass(frozen=True, slots=True)
class Session:
    """A scheduled session; an unknown end is never an estimated duration.

    CF schedule feeds do not establish provider session IDs or status fields.
    The internal ID identifies a named session within its race and season.
    """

    session_id: str
    name: str
    kind: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None
    notes: str | None = None
    run_type_code: int | None = None


@dataclass(frozen=True, slots=True)
class Race:
    """Stable schedule identity with optional known timing/track fields."""

    series_id: int
    race_id: int
    name: str
    start_time: datetime | None = None
    track: str | None = None
    season: int | None = None
    track_id: int | None = None
    sessions: tuple[Session, ...] = ()
    status: str | None = None
    sessions_failed: bool = False


@dataclass(frozen=True, slots=True)
class LiveSnapshot:
    """A single feed's session context, not proof the race is currently active."""

    series_id: int
    race_id: int
    status: str | None = None
    flag: str | None = None
    lap: int | None = None
    source_updated_at: datetime | None = None
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), compare=False
    )
    run_id: int | None = None
    run_name: str | None = None
    total_laps: int | None = None
    laps_remaining: int | None = None
    elapsed_seconds: int | None = None
    leaderboard: Leaderboard | None = None
    leaderboard_failed: bool = False
    stage: CurrentStage | None = None
    stage_failed: bool = False
    run_type_code: int | None = None
    flag_state_code: int | None = None

    @property
    def session_key(self) -> tuple[int, int, int | None]:
        """Reported run identity; missing run IDs do not become invented IDs."""
        return self.series_id, self.race_id, self.run_id


def _integer(value: object, *, positive: bool = False) -> int | None:
    """Accept JSON integers and lossless decimal integer strings, not booleans."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and value.isdecimal():
        try:
            result = int(value)
        except ValueError:
            return None
    else:
        return None
    return result if result >= int(positive) else None


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _timestamp(value: object) -> datetime | None:
    """Require explicit timezone: the feed's naive dates have no proven zone."""
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value)
        if result.utcoffset() is None:
            return None
        return result.astimezone(UTC)
    except ValueError, OverflowError:
        return None


def _session(
    row: dict[str, object],
    series_id: int,
    race_id: int,
    season: int | None,
    *,
    detailed: bool = False,
) -> Session:
    """Normalize evidence-backed event fields without using time as identity."""
    name = _text(row.get("event_name"))
    if name is None:
        raise SchemaError("Schedule session has no name")
    run_type = _integer(row.get("run_type"))
    kind = (
        {1: "practice", 2: "qualifying", 3: "race"}.get(run_type)
        if run_type is not None
        else None
    )
    # No ordinal/time in identity: rescheduling and provider row order must not
    # create a new event. Indistinguishable duplicate names are rejected below.
    key = f"{run_type}:{name.casefold()}"
    digest = sha256(key.encode()).hexdigest()[:24]
    session_id = f"{series_id}:{season or 'unknown'}:{race_id}:{digest}"
    start = _timestamp(row.get("start_time_utc"))
    end = _timestamp(row.get("end_time_utc")) if detailed else None
    if start is None or end is not None and end <= start:
        end = None
    return Session(
        session_id=session_id,
        name=name,
        kind=kind,
        start_time=start,
        end_time=end,
        notes=_text(row.get("notes")) if not detailed else None,
        run_type_code=run_type,
    )


def _sessions(
    payload: object, series_id: int, race_id: int, season: int | None
) -> tuple[Session, ...]:
    """Read optional nested sessions; ambiguous identities cannot be guessed."""
    if payload is None:
        return ()
    if not isinstance(payload, list) or len(payload) > 100:
        raise SchemaError("Unexpected schedule session list")
    sessions: list[Session] = []
    seen: set[str] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise SchemaError("Invalid schedule session")
        session = _session(row, series_id, race_id, season)
        if session.session_id in seen:
            raise SchemaError("Ambiguous duplicate schedule session identity")
        seen.add(session.session_id)
        sessions.append(session)
    return tuple(sessions)


def parse_schedule(
    payload: object, series_id: int, *, year: int | None = None
) -> tuple[Race, ...]:
    """Read the documented global race-list envelope for exactly one series."""
    if series_id not in (1, 2, 3):
        raise ValueError("Unsupported national series")
    if not isinstance(payload, dict):
        raise SchemaError("Unexpected schedule envelope")
    rows = payload.get(f"series_{series_id}")
    if not isinstance(rows, list) or len(rows) > 500:
        raise SchemaError("Requested series is absent from the schedule")
    races: list[Race] = []
    seen: set[int] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise SchemaError("Invalid schedule race")
        race_id = _integer(row.get("race_id"), positive=True)
        row_series = _integer(row.get("series_id"), positive=True)
        name = _text(row.get("race_name"))
        if race_id is None or row_series != series_id or name is None:
            raise SchemaError("Schedule race has invalid identity")
        if race_id in seen:
            raise SchemaError("Duplicate schedule race identity")
        seen.add(race_id)
        season = _integer(row.get("race_season"), positive=True)
        if season is not None and not 1948 <= season <= 9999:
            season = None
        if year is not None and season is not None and season != year:
            raise SchemaError("Schedule race belongs to another season")
        season = season or year
        sessions_failed = False
        try:
            sessions = _sessions(row.get("schedule"), series_id, race_id, season)
        except SchemaError:
            # Session enrichment is optional. Schema drift here must not hide
            # the independently valid core race identity or known race time.
            sessions = ()
            sessions_failed = True
        races.append(
            Race(
                series_id=series_id,
                race_id=race_id,
                name=name,
                start_time=_timestamp(row.get("date_scheduled")),
                track=_text(row.get("track_name")),
                season=season,
                track_id=_integer(row.get("track_id"), positive=True),
                sessions=sessions,
                sessions_failed=sessions_failed,
            )
        )
    return tuple(races)


def parse_schedule_feed(payload: object, series_id: int, year: int) -> tuple[Race, ...]:
    """Read the third-party documented per-series session-array contract.

    Only explicit-offset UTC-named timestamps are used. Local start_time and
    end_time fields have no independently verified timezone and are ignored.
    """
    if series_id not in (1, 2, 3) or not 1948 <= year <= 9999:
        raise ValueError("Invalid NASCAR series or season")
    if not isinstance(payload, list) or len(payload) > 5000:
        raise SchemaError("Unexpected session schedule envelope")
    races: dict[int, Race] = {}
    sessions: dict[int, list[Session]] = {}
    seen: set[str] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise SchemaError("Invalid session schedule row")
        race_id = _integer(row.get("race_id"), positive=True)
        row_series = _integer(row.get("series_id"), positive=True)
        name = _text(row.get("race_name"))
        if race_id is None or row_series != series_id or name is None:
            raise SchemaError("Session schedule has invalid race identity")
        session = _session(row, series_id, race_id, year, detailed=True)
        if session.session_id in seen:
            raise SchemaError("Ambiguous duplicate schedule session identity")
        seen.add(session.session_id)
        track_id = _integer(row.get("track_id"), positive=True)
        track = _text(row.get("track_name"))
        prior = races.get(race_id)
        if prior is not None and (
            prior.name != name
            or prior.track_id is not None
            and track_id not in (None, prior.track_id)
        ):
            raise SchemaError("Session schedule has conflicting race metadata")
        races[race_id] = Race(
            series_id,
            race_id,
            name,
            track=track or (prior.track if prior is not None else None),
            season=year,
            track_id=track_id or (prior.track_id if prior is not None else None),
        )
        sessions.setdefault(race_id, []).append(session)
    return tuple(
        replace(
            race,
            start_time=_race_session_start(tuple(sessions[race_id])),
            sessions=tuple(sessions[race_id]),
        )
        for race_id, race in races.items()
    )


def _race_session_start(sessions: tuple[Session, ...]) -> datetime | None:
    """Only a single race session can unambiguously supply the race start."""
    race_sessions = [session for session in sessions if session.kind == "race"]
    return race_sessions[0].start_time if len(race_sessions) == 1 else None


def merge_schedule(
    basic: tuple[Race, ...], detailed: tuple[Race, ...]
) -> tuple[Race, ...]:
    """Replace each published weekend's sessions, retaining basic-only races."""
    races = {(race.series_id, race.season, race.race_id): race for race in basic}
    for race in detailed:
        key = (race.series_id, race.season, race.race_id)
        prior = races.get(key)
        if prior is None:
            races[key] = race
            continue
        if (
            prior.track_id is not None
            and race.track_id is not None
            and prior.track_id != race.track_id
        ):
            raise SchemaError("Schedule sources have conflicting track identities")
        notes = {session.session_id: session.notes for session in prior.sessions}
        has_race_session = any(session.kind == "race" for session in race.sessions)
        races[key] = replace(
            prior,
            name=race.name,
            # A published race session whose start is now unknown/ambiguous
            # supersedes an older basic timestamp. Retaining that old time
            # would turn a TBD/postponed start into a misleading next race.
            start_time=race.start_time if has_race_session else prior.start_time,
            track=race.track or prior.track,
            track_id=race.track_id or prior.track_id,
            sessions=tuple(
                replace(session, notes=session.notes or notes.get(session.session_id))
                for session in race.sessions
            ),
            sessions_failed=False,
        )
    return tuple(races.values())


def parse_live(payload: object) -> LiveSnapshot | None:
    """Normalize a single live feed; unknown flag/type codes remain unknown."""
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise SchemaError("Unexpected live feed envelope")
    series_id = _integer(payload.get("series_id"), positive=True)
    race_id = _integer(payload.get("race_id"), positive=True)
    if series_id not in (1, 2, 3) or race_id is None:
        raise SchemaError("Live feed has invalid identity")
    flags = {
        1: "green",
        2: "yellow",
        3: "red",
        4: "white",
        5: "checkered",
        8: "hot_track",
        9: "cold_track",
    }
    run_types = {1: "practice", 2: "qualifying", 3: "race"}
    run_type = _integer(payload.get("run_type"))
    flag_state = _integer(payload.get("flag_state"))
    run_name = _text(payload.get("run_name"))
    leaderboard = None
    leaderboard_failed = False
    if "vehicles" in payload:
        try:
            leaderboard = parse_leaderboard(payload["vehicles"])
        except ValueError:
            # Optional scoring drift cannot discard independent flag/lap data.
            leaderboard_failed = True
    stage = None
    stage_failed = False
    if run_type == 3 and "stage" in payload:
        try:
            stage = parse_current_stage(payload["stage"])
        except ValueError:
            stage_failed = True
    return LiveSnapshot(
        series_id=series_id,
        race_id=race_id,
        status=run_types.get(run_type) if run_type is not None else None,
        flag=flags.get(flag_state) if flag_state is not None else None,
        lap=_integer(payload.get("lap_number")),
        source_updated_at=_timestamp(payload.get("time_of_day_os")),
        run_id=_integer(payload.get("run_id"), positive=True),
        run_name=run_name[:160] if run_name is not None else None,
        total_laps=_integer(payload.get("laps_in_race"), positive=True)
        if run_type == 3
        else None,
        laps_remaining=_integer(payload.get("laps_to_go")) if run_type == 3 else None,
        elapsed_seconds=_integer(payload.get("elapsed_time")),
        leaderboard=leaderboard,
        leaderboard_failed=leaderboard_failed,
        stage=stage,
        stage_failed=stage_failed,
        run_type_code=run_type,
        flag_state_code=flag_state,
    )
