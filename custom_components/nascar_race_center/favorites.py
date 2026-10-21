"""Stable favorite-driver identities shared with future live timing features."""

from collections.abc import Mapping

from .reference import Driver

MAX_FAVORITE_DRIVERS = 50


def normalize_favorite_driver_ids(values: object) -> tuple[int, ...]:
    """Validate persisted NASCAR IDs without depending on a current directory.

    An absent driver directory must never erase a user's selection. Directory
    membership therefore is not a validation requirement, and names/car numbers
    are never accepted as identity. Bounds prevent accidental entity explosions.
    """
    if not isinstance(values, list | tuple):
        raise ValueError("Favorite drivers must be a list of NASCAR driver IDs")
    ids: set[int] = set()
    for value in values:
        if (
            not isinstance(value, str)
            or not value.isascii()
            or not value.isdecimal()
            or len(value) > 20
            or int(value) <= 0
        ):
            raise ValueError("Invalid NASCAR driver ID")
        ids.add(int(value))
    if len(ids) > MAX_FAVORITE_DRIVERS:
        raise ValueError("Too many favorite drivers")
    return tuple(sorted(ids))


class FavoriteDriverRegistry:
    """Keep immutable selections independent of team, number, name or series."""

    def __init__(self, values: object = ()) -> None:
        """Normalize IDs once per config-entry runtime; spawn no background tasks."""
        self._ids = normalize_favorite_driver_ids(values)
        self._selected = frozenset(self._ids)

    @property
    def ids(self) -> tuple[int, ...]:
        """Return deterministic IDs, including drivers missing from the directory."""
        return self._ids

    def contains(self, driver_id: int) -> bool:
        """Test a Phase 3 observation against stable NASCAR identity."""
        return driver_id in self._selected

    def get(self, driver_id: int, drivers: Mapping[int, Driver]) -> Driver | None:
        """Resolve current metadata without replacing a missing selected ID."""
        return drivers.get(driver_id) if self.contains(driver_id) else None

    def selected(self, drivers: Mapping[int, Driver]) -> tuple[Driver, ...]:
        """Return available metadata for selected IDs, independent of series."""
        return tuple(
            drivers[driver_id] for driver_id in self.ids if driver_id in drivers
        )
