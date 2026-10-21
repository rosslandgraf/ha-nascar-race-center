"""Entry-owned HA event delivery; no notification or device services."""

import asyncio
import logging
from collections import deque
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCHEDULE_STALE_AFTER
from .coordinator import LiveCoordinator, ScheduleCoordinator
from .events import EVENT_NAMESPACE, EventEngine, EventPreferences, RacingEvent
from .models import LiveSnapshot

_LOGGER = logging.getLogger(__name__)
MAX_PENDING = 32


class EventRuntime:
    """Serialize a bounded queue, saving replay barriers before bus publication."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        live: LiveCoordinator,
        schedule: ScheduleCoordinator,
        preferences: EventPreferences,
        source: str,
    ) -> None:
        self.hass = hass
        self.live = live
        self.schedule = schedule
        self.engine = EventEngine(preferences, source)
        self.store: Store[dict[str, Any]] = Store(
            hass, 1, f"{DOMAIN}.{entry.entry_id}.events", private=True
        )
        self._unsubs: list[Callable[[], None]] = []
        self._timer: Callable[[], None] | None = None
        self._queue: deque[tuple[bool, LiveSnapshot | None, bool, datetime]] = deque()
        self._task: asyncio.Task[None] | None = None
        self._stopped = False
        self._epoch = 0
        self.status = "disabled"
        entry.async_on_unload(self.async_shutdown)

    async def async_start(self) -> None:
        """Restore only deduplication, then silently baseline the current sources."""
        if not self.engine.preferences.enabled:
            return
        try:
            existed = await self.hass.async_add_executor_job(
                Path(self.store.path).is_file
            )
            data = await self.store.async_load()
            if existed and data is None:
                raise ValueError("Event ledger was empty or corrupt")
            if data is not None:
                self.engine.restore(data)
            self.engine.observe(
                self.live.data, valid=self._live_valid(), now=dt_util.utcnow()
            )
            self._observe_schedule()
            await self.store.async_save(self.engine.export())
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            HomeAssistantError,
            NotImplementedError,
        ):
            # Fail closed for this load. Existing entity/coordinator operation
            # remains available; a broken ledger cannot silently re-enable events.
            _LOGGER.error(
                "Racing events disabled: event ledger could not be loaded or saved"
            )
            self._stopped = True
            self.status = "ledger_error"
            self._cancel_timer()
            return
        self._unsubs = [
            self.live.async_add_listener(self._live_changed),
            self.schedule.async_add_listener(self._schedule_changed),
        ]
        self.status = "ready"

    def _live_valid(self) -> bool:
        snapshot = self.live.data
        return snapshot is not None and self.live.view(snapshot.series_id).available

    @callback
    def _live_changed(self) -> None:
        if not self._live_valid():
            self._epoch += 1
        self._enqueue(True)

    @callback
    def _schedule_changed(self) -> None:
        self._enqueue(False)

    @callback
    def _enqueue(self, live: bool) -> None:
        if self._stopped:
            return
        if len(self._queue) >= MAX_PENDING:
            self._queue.clear()
            self.engine.invalidate()
            self._epoch += 1
        self._queue.append((live, self.live.data, self._live_valid(), dt_util.utcnow()))
        if self._task is None:
            self._task = self.hass.async_create_task(
                self._async_process(), "NASCAR event delivery", eager_start=False
            )

    def _observe_schedule(self) -> tuple[RacingEvent, ...]:
        now = dt_util.utcnow()
        races = tuple(
            race
            for series in self.schedule.series
            if (updated := self.schedule.data.updated_at.get(series)) is not None
            and datetime.min.replace(tzinfo=dt_util.UTC) <= updated <= now
            and now - updated <= SCHEDULE_STALE_AFTER
            for race in self.schedule.usable_races(series)
            if race.series_id == series
        )
        events = self.engine.reminders(races, now)
        self._cancel_timer()
        deadline = self.engine.next_reminder(now)
        if deadline is not None and not self._stopped:
            self._timer = async_track_point_in_utc_time(
                self.hass, self._reminder_due, deadline
            )
        return events

    @callback
    def _reminder_due(self, now: datetime) -> None:
        self._timer = None
        self._enqueue(False)

    async def _async_process(self) -> None:
        try:
            while self._queue and not self._stopped:
                live, snapshot, valid, now = self._queue.popleft()
                epoch = self._epoch
                before = self.engine.export()
                events = (
                    self.engine.observe(snapshot, valid=valid, now=now)
                    if live
                    else self._observe_schedule()
                )
                after = self.engine.export()
                if before != after:
                    try:
                        await self.store.async_save(after)
                    except OSError, ValueError, HomeAssistantError:
                        _LOGGER.error(
                            "Racing events disabled: event ledger save failed"
                        )
                        self._stopped = True
                        self.status = "ledger_error"
                        self._queue.clear()
                        self._cancel_timer()
                        for unsub in self._unsubs:
                            unsub()
                        self._unsubs.clear()
                        return
                if self._stopped or epoch != self._epoch:
                    continue
                for event in events:
                    # A source outage/switch during disk I/O invalidates delivery.
                    if live and (
                        not self._live_valid()
                        or self.live.data is None
                        or self.live.data.session_key
                        != (event.series_id, event.race_id, event.run_id)
                    ):
                        continue
                    self.hass.bus.async_fire(EVENT_NAMESPACE, event.payload())
        finally:
            self._task = None

    def _cancel_timer(self) -> None:
        if self._timer is not None:
            self._timer()
            self._timer = None

    async def async_shutdown(self) -> None:
        """Stop callbacks and await/cancel in-flight storage work before unload."""
        self._stopped = True
        if self.status != "ledger_error":
            self.status = "stopped"
        self._epoch += 1
        self._cancel_timer()
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        self._queue.clear()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
