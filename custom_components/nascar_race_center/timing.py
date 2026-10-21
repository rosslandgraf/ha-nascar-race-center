"""Immutable reported field and narrow experimental vehicle parser.

Community evidence and intentionally unresolved semantics: PHASE3A_LIVE.md.
No entities, HTTP, retained histories or inferred retirement/result states here.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class LedInterval:
    """Reported boundaries; inclusivity and unfinished intervals are unverified."""

    start_lap: int
    end_lap: int


@dataclass(frozen=True, slots=True)
class LiveDriver:
    """One reported competitor, identified only by NASCAR driver ID."""

    driver_id: int
    name: str | None = None
    car_number: str | None = None
    manufacturer: str | None = None
    position: int | None = None
    starting_position: int | None = None
    laps_completed: int | None = None
    last_lap_time: float | None = None
    best_lap_time: float | None = None
    last_lap_speed: float | None = None
    best_lap_speed: float | None = None
    average_speed: float | None = None
    gap: float | None = None
    status_code: int | None = None
    is_on_track: bool | None = None
    laps_led: tuple[LedInterval, ...] | None = None

    @property
    def running_status(self) -> str | None:
        """Only the community-documented running code has a known meaning."""
        return "running" if self.status_code == 1 else None

    @property
    def position_change(self) -> int | None:
        """Derive gain relative to supplied grid position, never a previous poll."""
        if self.starting_position is None or self.position is None:
            return None
        return self.starting_position - self.position


@dataclass(frozen=True, slots=True)
class Leaderboard:
    """One immutable ordered field with O(1) NASCAR-ID lookup.

    Missing/unranked positions sort after reported positions. Duplicate ranks do
    not imply a tiebreaker or a leader. Missing driver IDs are counted as omitted,
    never substituted with vehicle number/name. This is the reported field, not
    a claim of a complete entry list or final classification.
    """

    drivers: tuple[LiveDriver, ...]
    reported_count: int
    omitted_count: int = 0
    by_driver: Mapping[int, LiveDriver] = field(init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        """Reject ambiguous identities and construct a read-only lookup once."""
        lookup = {driver.driver_id: driver for driver in self.drivers}
        if len(lookup) != len(self.drivers):
            raise ValueError("Duplicate live driver identity")
        object.__setattr__(self, "by_driver", MappingProxyType(lookup))

    @property
    def leader(self) -> LiveDriver | None:
        """A unique reported first position is required; never select list head."""
        leaders = [driver for driver in self.drivers if driver.position == 1]
        return leaders[0] if len(leaders) == 1 else None


def _count(value: object, *, positive: bool = False) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, str) and value.isascii() and value.isdecimal():
        value = int(value) if len(value) <= 20 else None
    return (
        value if isinstance(value, int) and int(positive) <= value <= 10**20 else None
    )


def _number(value: object, *, positive: bool = False) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        return None
    try:
        number = float(value)
    except ValueError, OverflowError:
        return None
    if not isfinite(number) or positive and number <= 0:
        return None
    return number


def _text(value: object) -> str | None:
    return (
        value.strip()
        if isinstance(value, str) and 0 < len(value.strip()) <= 160
        else None
    )


def _intervals(value: object) -> tuple[LedInterval, ...] | None:
    if not isinstance(value, list) or len(value) > 1000:
        return None
    result: list[LedInterval] = []
    for row in value:
        if not isinstance(row, dict):
            return None
        start, end = _count(row.get("start_lap")), _count(row.get("end_lap"))
        if start is None or end is None or end < start:
            return None
        result.append(LedInterval(start, end))
    return tuple(result)


def parse_leaderboard(payload: object) -> Leaderboard:
    """Normalize only the documented vehicles array, tolerating optional gaps."""
    if not isinstance(payload, list) or len(payload) > 100:
        raise ValueError("Unexpected live vehicles envelope")
    drivers: list[LiveDriver] = []
    for row in payload:
        if not isinstance(row, dict) or not isinstance(row.get("driver"), dict):
            continue
        driver = row["driver"]
        driver_id = _count(driver.get("driver_id"), positive=True)
        if driver_id is None:
            continue
        car = row.get("vehicle_number")
        car_number = (
            str(car)
            if isinstance(car, int) and not isinstance(car, bool)
            else _text(car)
        )
        manufacturer = _text(row.get("vehicle_manufacturer"))
        if manufacturer and ("/" in manufacturer or ":" in manufacturer):
            manufacturer = None
        drivers.append(
            LiveDriver(
                driver_id=driver_id,
                name=_text(driver.get("full_name")),
                car_number=car_number if car_number and len(car_number) <= 8 else None,
                manufacturer=manufacturer,
                position=_count(row.get("running_position"), positive=True),
                starting_position=_count(row.get("starting_position"), positive=True),
                laps_completed=_count(row.get("laps_completed")),
                last_lap_time=_number(row.get("last_lap_time"), positive=True),
                best_lap_time=_number(row.get("best_lap_time"), positive=True),
                last_lap_speed=_number(row.get("last_lap_speed"), positive=True),
                best_lap_speed=_number(row.get("best_lap_speed"), positive=True),
                average_speed=_number(row.get("average_speed"), positive=True),
                gap=_number(row.get("delta")),
                status_code=_count(row.get("status")),
                is_on_track=row.get("is_on_track")
                if isinstance(row.get("is_on_track"), bool)
                else None,
                laps_led=_intervals(row.get("laps_led")),
            )
        )
    if payload and not drivers:
        raise ValueError("Live field has no usable driver identities")
    drivers.sort(
        key=lambda driver: (
            driver.position is None,
            driver.position or 0,
            driver.driver_id,
        )
    )
    return Leaderboard(tuple(drivers), len(payload), len(payload) - len(drivers))
