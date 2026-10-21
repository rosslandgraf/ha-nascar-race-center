"""Immutable reference metadata with conservative, documented CF parsing.

The directory is not an active roster. Provider metadata is associated only
with the series explicitly reported by a row; identity always uses NASCAR ID.
See docs/SCHEMA_EVIDENCE.md for third-party shape evidence and its limitations.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast

from .models import SchemaError, _integer

MAX_DRIVER_ROWS = 10000
MAX_TRACK_ROWS = 1000
_SERIES_SLUGS = {
    "nascar-cup-series": 1,
    "nascar-xfinity-series": 2,
    "nascar-craftsman-truck-series": 3,
}


@dataclass(frozen=True, slots=True)
class DriverAssociation:
    """One reported directory association, without claiming current entry."""

    series_id: int | None = None
    series_label: str | None = None
    car_number: str | None = None
    team: str | None = None
    manufacturer: str | None = None
    # Numeric Team strings have no verified display-name or join semantics.
    team_raw: str | None = None


@dataclass(frozen=True, slots=True)
class Driver:
    """Stable NASCAR identity and unambiguous optional directory metadata."""

    driver_id: int
    name: str
    series_ids: tuple[int, ...] = ()
    car_number: str | None = None
    team: str | None = None
    manufacturer: str | None = None
    associations: tuple[DriverAssociation, ...] = ()
    series_label: str | None = None

    def association_for(self, series_id: int) -> DriverAssociation | None:
        """Return series metadata only when a single reported row is clear."""
        matches = [item for item in self.associations if item.series_id == series_id]
        return matches[0] if len(matches) == 1 else None


@dataclass(frozen=True, slots=True)
class Track:
    """Venue facts supported by the documented track reference shape."""

    track_id: int
    name: str
    city: str | None = None
    state: str | None = None
    length_miles: float | None = None
    track_type: str | None = None
    surface: str | None = None

    @property
    def location(self) -> str | None:
        """Join only supplied locality values; never infer a timezone."""
        return ", ".join(part for part in (self.city, self.state) if part) or None


def _text(value: object, limit: int = 160) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value if value and len(value) <= limit else None


def _manufacturer(value: object) -> str | None:
    """Some rows contain a logo URL; a URL does not establish a brand name."""
    text = _text(value)
    if text is None or "://" in text or text.startswith(("/", "www.")):
        return None
    return text


def _team_name(value: object) -> str | None:
    """Keep textual labels; numeric strings are not verified team names."""
    text = _text(value)
    return text if text is not None and not text.isdecimal() else None


def _car_number(value: object) -> str | None:
    """Keep leading zeroes in documented numeric-string Badge values."""
    text = _text(value, 4)
    return text if text is not None and text.isascii() and text.isdecimal() else None


def _identity(value: object) -> int | None:
    """Treat malformed or oversized decimal strings as unusable identities."""
    try:
        return _integer(value, positive=True)
    except ValueError:
        return None


def _rows(payload: object, key: str, maximum: int) -> list[object]:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), list):
        raise SchemaError("Unexpected reference feed envelope")
    rows = cast(list[object], payload[key])
    if len(rows) > maximum:
        raise SchemaError("Reference feed exceeded the record limit")
    return rows


def _consensus(values: Iterable[str | None]) -> str | None:
    options = set(values)
    return options.pop() if len(options) == 1 else None


def parse_drivers(payload: object) -> tuple[Driver, ...]:
    """Read documented rows, grouping multi-series records by NASCAR ID.

    Records without a stable NASCAR ID/name cannot become entities. They are
    ignored, but a nonempty directory with no usable identities is a schema
    failure rather than a falsely empty database. Conflicting names for one
    NASCAR ID fail explicitly. No secondary ID or car number substitutes for ID.
    """
    rows = _rows(payload, "response", MAX_DRIVER_ROWS)
    names: dict[int, str] = {}
    grouped: dict[int, list[DriverAssociation]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        driver_id = _identity(row.get("Nascar_Driver_ID"))
        name = _text(row.get("Full_Name"))
        if driver_id is None or name is None:
            continue
        if driver_id in names and names[driver_id] != name:
            raise SchemaError("Conflicting reference driver identity")
        names[driver_id] = name
        label = _text(row.get("Driver_Series"))
        association = DriverAssociation(
            series_id=_SERIES_SLUGS.get(label) if label else None,
            series_label=label,
            car_number=_car_number(row.get("Badge")),
            team=_team_name(row.get("Team")),
            team_raw=_text(row.get("Team")),
            manufacturer=_manufacturer(row.get("Manufacturer")),
        )
        associations = grouped.setdefault(driver_id, [])
        if association not in associations:
            associations.append(association)
    if rows and not grouped:
        raise SchemaError("Reference directory has no usable driver identities")
    return tuple(
        Driver(
            driver_id=driver_id,
            name=names[driver_id],
            series_ids=tuple(
                sorted({item.series_id for item in rows if item.series_id is not None})
            ),
            car_number=_consensus(item.car_number for item in rows),
            team=_consensus(item.team for item in rows),
            manufacturer=_consensus(item.manufacturer for item in rows),
            associations=tuple(rows),
            series_label=", ".join(
                sorted({item.series_label for item in rows if item.series_label})
            )
            or None,
        )
        for driver_id, rows in sorted(grouped.items())
    )


def _positive_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (str, float, int)):
        return None
    try:
        number = float(value)
    except ValueError, OverflowError:
        return None
    return number if math.isfinite(number) and number > 0 else None


def parse_tracks(payload: object) -> tuple[Track, ...]:
    """Parse only documented physical facts, ignoring media and inferred data."""
    rows = _rows(payload, "items", MAX_TRACK_ROWS)
    tracks: dict[int, Track] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        track_id = _identity(row.get("track_id"))
        name = _text(row.get("track_name"))
        if track_id is None or name is None:
            continue
        track = Track(
            track_id=track_id,
            name=name,
            city=_text(row.get("city")),
            state=_text(row.get("state")),
            length_miles=_positive_number(row.get("length")),
            track_type=_text(row.get("track_type")),
            surface=_text(row.get("track_surface")),
        )
        if track_id in tracks and tracks[track_id] != track:
            raise SchemaError("Conflicting reference track identity")
        tracks[track_id] = track
    if rows and not tracks:
        raise SchemaError("Reference directory has no usable track identities")
    return tuple(tracks[key] for key in sorted(tracks))


def demo_drivers() -> tuple[Driver, ...]:
    """Supply fictional, clearly named choices without NASCAR data or I/O."""
    return (
        Driver(
            driver_id=99001,
            name="Demo Alex Driver",
            series_ids=(1, 2),
            associations=(
                DriverAssociation(1, "Demonstration Cup", "07", "Demo Racing"),
                DriverAssociation(2, "Demonstration Series 2", "17", "Demo Racing"),
            ),
            team="Demo Racing",
            series_label="Demonstration Cup, Demonstration Series 2",
        ),
        Driver(
            driver_id=99002,
            name="Demo Jordan Driver",
            series_ids=(2,),
            car_number="22",
            team="Example Motorsports",
            associations=(
                DriverAssociation(
                    2, "Demonstration Series 2", "22", "Example Motorsports"
                ),
            ),
            series_label="Demonstration Series 2",
        ),
        Driver(
            driver_id=99003,
            name="Demo Taylor Driver",
            series_ids=(3,),
            car_number="03",
            team="Sample Racing",
            associations=(
                DriverAssociation(3, "Demonstration Trucks", "03", "Sample Racing"),
            ),
            series_label="Demonstration Trucks",
        ),
    )


def demo_tracks() -> tuple[Track, ...]:
    """Fictional venue data never represents a real NASCAR venue."""
    return (
        Track(
            track_id=99001,
            name="Demonstration Speedway",
            city="Example City",
            state="Example State",
            length_miles=1.5,
            track_type="Demonstration oval",
            surface="Asphalt",
        ),
    )
