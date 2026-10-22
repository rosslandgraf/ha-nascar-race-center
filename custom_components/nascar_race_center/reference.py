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
    "nascar-oreilly-auto-parts-series": 2,
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


def _merge_associations(
    rows: Iterable[tuple[DriverAssociation, int]],
) -> tuple[DriverAssociation, ...]:
    """Prefer published rows per series; fill only compatible missing facts."""
    groups: dict[
        tuple[int | None, str | None], list[tuple[DriverAssociation, int]]
    ] = {}
    for association, rank in rows:
        key = (
            association.series_id,
            None if association.series_id else association.series_label,
        )
        groups.setdefault(key, []).append((association, rank))
    result: list[DriverAssociation] = []
    for group in groups.values():
        best = max(rank for _, rank in group)
        candidates = {item for item, rank in group if rank == best}
        facts = [
            {value for item in candidates if (value := getattr(item, key)) is not None}
            for key in ("car_number", "team", "manufacturer")
        ]
        if any(len(values) > 1 for values in facts):
            # Preserve competing metadata; association_for refuses to pick one.
            result.extend(candidates)
            continue
        labels = sorted(item.series_label for item in candidates if item.series_label)
        raw = {item.team_raw for item in candidates if item.team_raw}
        car, team, manufacturer = (next(iter(values), None) for values in facts)
        result.append(
            DriverAssociation(
                series_id=next(iter(candidates)).series_id,
                series_label=labels[0] if labels else None,
                car_number=car,
                team=team,
                manufacturer=manufacturer,
                team_raw=team or (next(iter(raw)) if len(raw) == 1 else None),
            )
        )
    return tuple(
        sorted(
            result,
            key=lambda item: (
                item.series_id or 0,
                item.series_label or "",
                item.car_number or "",
                item.team or "",
                item.manufacturer or "",
                item.team_raw or "",
            ),
        )
    )


def parse_drivers(
    payload: object, *, diagnostics: dict[str, object] | None = None
) -> tuple[Driver, ...]:
    """Quarantine ambiguous NASCAR IDs, preserving independently usable drivers.

    Case/whitespace variants are cosmetic; different spellings/initials are not
    guessed to identify the same person. Driver_ID/car/name never replace ID.
    Draft-only entries are directory facts, never proof of active participation.
    """
    rows = _rows(payload, "response", MAX_DRIVER_ROWS)
    names: dict[int, set[str]] = {}
    grouped: dict[int, set[tuple[DriverAssociation, int]]] = {}
    counts = dict.fromkeys(
        (
            "invalid_id_rows",
            "missing_name_rows",
            "non_object_rows",
            "draft_rows",
            "published_rows",
            "unknown_series_rows",
            "duplicate_association_rows",
            "numeric_team_rows",
        ),
        0,
    )
    for row in rows:
        if not isinstance(row, dict):
            counts["non_object_rows"] += 1
            continue
        driver_id = _identity(row.get("Nascar_Driver_ID"))
        name = _text(row.get("Full_Name"))
        if driver_id is None or driver_id >= 10**20:
            counts["invalid_id_rows"] += 1
            continue
        if name is None:
            counts["missing_name_rows"] += 1
            continue
        names.setdefault(driver_id, set()).add(" ".join(name.split()))
        label = _text(row.get("Driver_Series"))
        status = (_text(row.get("Driver_Post_Status")) or "").casefold()
        rank = {"publish": 2, "draft": 0}.get(status, 1)
        if status in {"publish", "draft"}:
            counts["published_rows" if status == "publish" else "draft_rows"] += 1
        association = DriverAssociation(
            series_id=_SERIES_SLUGS.get(label) if label else None,
            series_label=label,
            car_number=_car_number(row.get("Badge")),
            team=_team_name(row.get("Team")),
            team_raw=_text(row.get("Team")),
            manufacturer=_manufacturer(row.get("Manufacturer")),
        )
        counts["unknown_series_rows"] += int(association.series_id is None)
        counts["numeric_team_rows"] += int(
            association.team_raw is not None and association.team_raw.isdecimal()
        )
        ranked_rows = grouped.setdefault(driver_id, set())
        if (association, rank) in ranked_rows:
            counts["duplicate_association_rows"] += 1
        else:
            ranked_rows.add((association, rank))
    ambiguous = sorted(
        key
        for key, values in names.items()
        if len({value.casefold() for value in values}) > 1
    )
    rejected = set(ambiguous)
    drivers: list[Driver] = []
    for driver_id, entries in sorted(grouped.items()):
        if driver_id in rejected:
            continue
        associations = _merge_associations(entries)
        drivers.append(
            Driver(
                driver_id=driver_id,
                name=sorted(names[driver_id])[0],
                series_ids=tuple(
                    sorted(
                        {
                            item.series_id
                            for item in associations
                            if item.series_id is not None
                        }
                    )
                ),
                car_number=_consensus(item.car_number for item in associations),
                team=_consensus(item.team for item in associations),
                manufacturer=_consensus(item.manufacturer for item in associations),
                associations=associations,
                series_label=", ".join(
                    sorted(
                        {
                            item.series_label
                            for item in associations
                            if item.series_label
                        }
                    )
                )
                or None,
            )
        )
    if diagnostics is not None:
        diagnostics.clear()
        diagnostics.update(
            status="parsed_with_rejections"
            if ambiguous
            or any(
                counts[key]
                for key in ("invalid_id_rows", "missing_name_rows", "non_object_rows")
            )
            else "parsed",
            source_rows=len(rows),
            candidate_driver_ids=len(grouped),
            usable_driver_ids=len(drivers),
            ambiguous_driver_id_count=len(ambiguous),
            ambiguous_driver_ids_sample=ambiguous[:20],
            usable_driver_ids_sample=[driver.driver_id for driver in drivers[:20]],
            **counts,
        )
    if rows and not drivers:
        raise SchemaError("Reference directory has no usable driver identities")
    return tuple(drivers)


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
