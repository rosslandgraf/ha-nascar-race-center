"""Read-only native calendars built from normalized schedules.

An unknown duration is represented by a clearly labeled date marker. It never
becomes a guessed race length. Weekend markers describe the local dates of
published sessions, not a claim of uninterrupted racing across those dates.
"""

from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime, timedelta

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.components.calendar.const import CalendarEntityFeature
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from . import NascarConfigEntry
from .const import DOMAIN, REFERENCE_STALE_AFTER
from .entity import ScheduleEntity
from .models import Race, Session

_CANCELED = {"canceled", "cancelled"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NascarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Expose one native calendar for each selected national series."""
    async_add_entities(
        NascarSeriesCalendar(entry, series_id)
        for series_id in entry.runtime_data.schedule.series
    )


def _known_time(value: datetime | None) -> bool:
    """Protect the calendar boundary from ambiguous provider timestamps."""
    return value is not None and value.utcoffset() is not None


def _local_dates(start: datetime, end: datetime | None) -> tuple[date, date] | None:
    """Derive inclusive dates with an exclusive end for calendar date markers."""
    try:
        first = dt_util.as_local(start).date()
        last = dt_util.as_local(end or start).date()
        # An exact midnight end belongs to the previous date, like HA's
        # exclusive end. A missing duration keeps the known start date only.
        if end is not None and end > start:
            last = dt_util.as_local(end - timedelta(microseconds=1)).date()
        exclusive = max(first, last) + timedelta(days=1)
        # HA compares calendar markers with UTC query bounds and arms alarms
        # at local midnight. Extreme years may not support both conversions.
        dt_util.as_utc(dt_util.start_of_local_day(first))
        dt_util.as_utc(dt_util.start_of_local_day(exclusive))
        return first, exclusive
    except ValueError, OverflowError:
        return None


class NascarSeriesCalendar(ScheduleEntity, CalendarEntity):
    """A stable series calendar with no direct I/O or writable-event support."""

    _attr_translation_key = "schedule"
    _attr_icon = "mdi:calendar-clock"
    _attr_supported_features = CalendarEntityFeature(0)

    def __init__(self, entry: NascarConfigEntry, series_id: int) -> None:
        """Share series identity, schedule freshness and coordinator updates."""
        super().__init__(entry, series_id, "calendar")
        self.entry = entry
        self._unsub_overlap: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Listen for optional track enrichment without extra HTTP requests."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.entry.runtime_data.reference.async_add_listener(
                self._handle_coordinator_update
            )
        )
        self._schedule_overlap_start()

    async def async_will_remove_from_hass(self) -> None:
        """Release overlap alarms as well as the native calendar alarms."""
        if self._unsub_overlap is not None:
            self._unsub_overlap()
            self._unsub_overlap = None
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update native calendar subscribers after schedule/reference changes."""
        self._schedule_overlap_start()
        super()._handle_coordinator_update()

    @callback
    def _schedule_overlap_start(self) -> None:
        """Advance sessions that start while another calendar event is selected.

        CalendarEntity owns the selected event's start/end alarms. This single
        supplemental timer follows other session starts, including overlaps.
        """
        if self._unsub_overlap is not None:
            self._unsub_overlap()
            self._unsub_overlap = None
        now = dt_util.utcnow()
        if not self.available:
            return
        current = self.event
        if current is None:
            return
        current_start = dt_util.as_utc(current.start_datetime_local)
        candidates = [
            dt_util.as_utc(event.start_datetime_local)
            for event in self._events()
            if now < dt_util.as_utc(event.start_datetime_local)
            and dt_util.as_utc(event.start_datetime_local) != current_start
            and not (event.uid or "").endswith(":weekend")
        ]
        if candidates:
            self._unsub_overlap = async_track_point_in_utc_time(
                self.hass, self._overlap_started, min(candidates)
            )

    @callback
    def _overlap_started(self, now: datetime) -> None:
        """Re-evaluate current session locally and arm the next overlap."""
        self._unsub_overlap = None
        self._handle_coordinator_update()

    def _track_details(self, race: Race) -> tuple[str | None, str | None]:
        """Enrich by stable track ID; reference failure cannot hide a schedule."""
        name = race.track
        location = None
        references = self.entry.runtime_data.reference.data
        updated = references.updated_at.get("tracks")
        if (
            "tracks" in references.failed_feeds
            or updated is None
            or dt_util.utcnow() - updated > REFERENCE_STALE_AFTER
        ):
            return name, location
        track = references.tracks.get(race.track_id) if race.track_id else None
        if track is not None:
            name = name or track.name
            location = track.location
        return name, location

    def _description(self, race: Race) -> str:
        """Keep useful normalized context, excluding raw responses and media."""
        track, location = self._track_details(race)
        details = [f"Series ID: {race.series_id}", f"Race ID: {race.race_id}"]
        if race.season is not None:
            details.append(f"Season: {race.season}")
        if track:
            details.append(f"Track: {track}")
        if location:
            details.append(f"Location: {location}")
        if race.track_id is not None:
            details.append(f"Track ID: {race.track_id}")
        if race.status:
            details.append(f"Status: {race.status}")
        return "\n".join(details)

    def _uid(self, race: Race, session_id: str) -> str:
        """Keep identity independent of names, start times and HA timezone."""
        season = str(race.season) if race.season is not None else "unknown"
        return f"{DOMAIN}:{race.series_id}:{season}:{race.race_id}:{session_id}"

    def _session_event(self, race: Race, session: Session) -> CalendarEvent | None:
        """Represent verified bounds exactly, or explicitly mark a known date."""
        if session.status in _CANCELED or not _known_time(session.start_time):
            return None
        start = session.start_time
        assert start is not None
        end = session.end_time
        try:
            start = dt_util.as_utc(start)
            dt_util.as_local(start)
            if _known_time(end) and end is not None:
                end = dt_util.as_utc(end)
                dt_util.as_local(end)
        except ValueError, OverflowError:
            return None
        description = [self._description(race), f"Session: {session.name}"]
        if session.kind:
            description.append(f"Session type: {session.kind}")
        description.append(f"Session ID: {session.session_id}")
        if session.status:
            description.append(f"Status: {session.status}")
        if session.notes:
            description.append(session.notes)
        track, location = self._track_details(race)
        place = ", ".join(part for part in (track, location) if part) or None
        summary = f"{race.name} — {session.name}"
        if _known_time(end) and end is not None and end > start:
            return CalendarEvent(
                start=start,
                end=end,
                summary=summary,
                description="\n".join(description),
                location=place,
                uid=self._uid(race, session.session_id),
            )
        bounds = _local_dates(start, None)
        if bounds is None:
            return None
        description.extend(
            (
                f"Known start: {dt_util.as_local(start).isoformat()}",
                "Duration is unconfirmed. This all-day marker identifies the "
                "local date only; it does not mean the session lasts all day.",
            )
        )
        return CalendarEvent(
            start=bounds[0],
            end=bounds[1],
            summary=f"{summary} (duration unconfirmed)",
            description="\n".join(description),
            location=place,
            uid=self._uid(race, session.session_id),
        )

    def _events(self) -> list[CalendarEvent]:
        """Build bounded in-memory events from the existing season cache."""
        events: list[CalendarEvent] = []
        for race in self.coordinator.data.races.get(self.series_id, ()):
            if race.status in _CANCELED or (
                race.season or dt_util.utcnow().year
            ) in self.coordinator.data.failed_seasons.get(self.series_id, frozenset()):
                continue
            sessions = race.sessions
            race_sessions = [session for session in sessions if session.kind == "race"]
            if not race_sessions:
                sessions = (
                    *sessions,
                    Session("race", "Race", kind="race", start_time=race.start_time),
                )
            elif len(race_sessions) == 1 and _known_time(race.start_time):
                # A detailed feed can omit/obscure its race timestamp while the
                # season list still has a verified offset-aware start. Preserve
                # the detailed session's identity without assigning this time
                # to multiple ambiguous race-kind sessions.
                sessions = tuple(
                    replace(
                        item,
                        start_time=race.start_time,
                        notes="\n".join(
                            part
                            for part in (
                                item.notes,
                                "Start from the season race schedule; detailed "
                                "session start is unavailable.",
                            )
                            if part
                        ),
                    )
                    if item.kind == "race" and not _known_time(item.start_time)
                    else item
                    for item in sessions
                )
            race_events = [
                event
                for session in sessions
                if (event := self._session_event(race, session)) is not None
            ]
            events.extend(race_events)
            if not race_events:
                continue
            first = min(event.start_datetime_local.date() for event in race_events)
            # All-day marker ends are already exclusive. Timed ends exactly at
            # midnight must not add a spurious extra weekend date.
            end_dates = []
            for event in race_events:
                if isinstance(event.start, datetime) and isinstance(
                    event.end, datetime
                ):
                    bounds = _local_dates(event.start, event.end)
                    if bounds is not None:
                        end_dates.append(bounds[1])
                else:
                    assert not isinstance(event.end, datetime)
                    end_dates.append(event.end)
            if not end_dates:
                continue
            last = max(end_dates)
            track, location = self._track_details(race)
            events.append(
                CalendarEvent(
                    start=first,
                    end=last,
                    summary=f"{race.name} — Race weekend (published dates)",
                    description=self._description(race)
                    + "\nDate range derived from published session dates in your "
                    "Home Assistant timezone; no continuous event duration is implied.",
                    location=", ".join(part for part in (track, location) if part)
                    or None,
                    uid=self._uid(race, "weekend"),
                )
            )
        return sorted(
            events,
            key=lambda event: (
                dt_util.as_utc(event.start_datetime_local),
                event.uid or "",
            ),
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Prefer an active session, then an active weekend, then upcoming data."""
        now = dt_util.utcnow()
        events = [
            event
            for event in self._events()
            if dt_util.as_utc(event.end_datetime_local) > now
        ]
        active = [
            event
            for event in events
            if dt_util.as_utc(event.start_datetime_local) <= now
        ]
        if active:
            return min(
                active,
                key=lambda event: (
                    event.all_day,
                    (event.uid or "").endswith(":weekend"),
                    dt_util.as_utc(event.end_datetime_local),
                    event.uid or "",
                ),
            )
        return events[0] if events else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return every overlapping event, with exclusive query/end boundaries."""
        if not self.available:
            raise HomeAssistantError("NASCAR schedule is unavailable")
        if not _known_time(start_date) or not _known_time(end_date):
            raise HomeAssistantError("Calendar query requires timezone-aware bounds")
        start_date = dt_util.as_utc(start_date)
        end_date = dt_util.as_utc(end_date)
        if end_date <= start_date:
            return []
        return [
            event
            for event in self._events()
            if dt_util.as_utc(event.start_datetime_local) < end_date
            and dt_util.as_utc(event.end_datetime_local) > start_date
        ]
