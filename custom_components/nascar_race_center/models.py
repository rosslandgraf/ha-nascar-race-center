"""Immutable normalized models and conservative CF parsing.

Field provenance is recorded in docs/SCHEMA_EVIDENCE.md. Optional fields can
vanish without inventing values; invalid identities/envelopes fail explicitly.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


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


@dataclass(frozen=True, slots=True)
class Race:
    """Stable schedule identity with optional known timing/track fields."""

    series_id: int
    race_id: int
    name: str
    start_time: datetime | None = None
    track: str | None = None


@dataclass(frozen=True, slots=True)
class LiveSnapshot:
    """A single feed's session context, not proof the race is currently active."""

    series_id: int
    race_id: int
    status: str | None = None
    flag: str | None = None
    lap: int | None = None
    source_updated_at: datetime | None = None
    observed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


def _integer(value: object, *, positive: bool = False) -> int | None:
    """Accept JSON integers and lossless decimal integer strings, not booleans."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and value.isdecimal():
        result = int(value)
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
    except ValueError:
        return None
    if result.utcoffset() is None:
        return None
    return result.astimezone(UTC)


def parse_schedule(payload: object, series_id: int) -> tuple[Race, ...]:
    """Read the documented global race-list envelope for exactly one series."""
    if series_id not in (1, 2, 3):
        raise ValueError("Unsupported national series")
    if not isinstance(payload, dict):
        raise SchemaError("Unexpected schedule envelope")
    rows = payload.get(f"series_{series_id}")
    if not isinstance(rows, list):
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
        races.append(
            Race(
                series_id=series_id,
                race_id=race_id,
                name=name,
                start_time=_timestamp(row.get("date_scheduled")),
                track=_text(row.get("track_name")),
            )
        )
    return tuple(races)


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
    return LiveSnapshot(
        series_id=series_id,
        race_id=race_id,
        status=run_types.get(run_type) if run_type is not None else None,
        flag=flags.get(flag_state) if flag_state is not None else None,
        lap=_integer(payload.get("lap_number")),
        source_updated_at=_timestamp(payload.get("time_of_day_os")),
    )
