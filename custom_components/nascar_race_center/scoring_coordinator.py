"""Independent optional-feed health; no data association based on receipt time."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .coordinator import LiveCoordinator
from .models import ProviderError
from .scoring import RaceContext, ScoringFeed, association_state
from .scoring_provider import SCORING_KINDS, ScoringKind, ScoringProvider

_LOGGER = logging.getLogger(__name__)
SCORING_INTERVAL = timedelta(minutes=15)
SCORING_IDLE_INTERVAL = timedelta(hours=6)


@dataclass(frozen=True)
class ScoringData:
    feeds: dict[ScoringKind, ScoringFeed]
    failed: frozenset[ScoringKind]
    errors: dict[ScoringKind, int | None]


class ScoringCoordinator(DataUpdateCoordinator[ScoringData]):
    """Three global requests, independent of series count and favorite count.

    HA owns shutdown through config_entry. No custom timers/tasks or persisted
    data. Local live-source expiry also notifies scoring listeners so trusted
    normalized sources cannot remain visible after their own clock expires.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        provider: ScoringProvider,
        live: LiveCoordinator,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="NASCAR optional scoring",
            update_interval=SCORING_IDLE_INTERVAL,
        )
        self.provider = provider
        self.live = live
        self.data = ScoringData({}, frozenset(), {})
        self._retry_at: dict[ScoringKind, datetime] = {}
        self._stopped = False
        self._remove_live_listener = live.async_add_listener(self._live_updated)
        self._unsub_expiry: Callable[[], None] | None = None

    @callback
    def _live_updated(self) -> None:
        if not self._stopped:
            self.async_update_listeners()

    async def async_shutdown(self) -> None:
        self._stopped = True
        self._remove_live_listener()
        if self._unsub_expiry is not None:
            self._unsub_expiry()
            self._unsub_expiry = None
        await super().async_shutdown()

    def capability(self, kind: ScoringKind, series_id: int) -> str:
        """A retained feed cannot silently become data for a different race."""
        view = self.live.view(series_id)
        if not view.available:
            return view.health
        if view.snapshot is None or view.snapshot.status != "race":
            return "not_race_session"
        if kind in self.data.failed:
            return "denied" if self.data.errors.get(kind) in {401, 403} else "offline"
        feed = self.data.feeds.get(kind)
        if feed is None:
            return "not_reported"
        active = RaceContext(
            view.snapshot.series_id,
            view.snapshot.race_id,
            view.snapshot.run_id,
            "live_timing",
        )
        state = association_state(feed, active, dt_util.utcnow())
        if state == "available" and not (feed.pits or feed.stages or feed.points):
            return "not_reported"
        return state

    def feed(self, kind: ScoringKind, series_id: int) -> ScoringFeed | None:
        """The consumer boundary supplies only validated current race data."""
        return (
            self.data.feeds.get(kind)
            if self.capability(kind, series_id) == "available"
            else None
        )

    @callback
    def _schedule_expiry(self, data: ScoringData | None = None) -> None:
        if self._unsub_expiry is not None:
            self._unsub_expiry()
            self._unsub_expiry = None
        if self._stopped:
            return
        now = dt_util.utcnow()
        deadlines = [
            feed.provenance.source_updated_at + timedelta(minutes=15, seconds=1)
            for feed in (data or self.data).feeds.values()
            if feed.provenance.source_updated_at is not None
            and feed.provenance.source_updated_at.utcoffset() is not None
            and feed.provenance.source_updated_at <= now + timedelta(minutes=5)
        ]
        future = [deadline for deadline in deadlines if deadline > now]
        if future:
            self._unsub_expiry = async_track_point_in_utc_time(
                self.hass, self._expired, min(future)
            )

    @callback
    def _expired(self, now: datetime) -> None:
        self._unsub_expiry = None
        if not self._stopped:
            self.async_update_listeners()
            self._schedule_expiry()

    async def _async_update_data(self) -> ScoringData:
        feeds = dict(self.data.feeds)
        failed = set(self.data.failed)
        errors = dict(self.data.errors)
        now = dt_util.utcnow()
        for kind in SCORING_KINDS:
            if self._retry_at.get(kind, now) > now:
                continue
            try:
                feed = await self.provider.async_get_scoring(kind)
            except ProviderError as err:
                failed.add(kind)
                errors[kind] = err.status
                self._retry_at[kind] = now + timedelta(seconds=err.retry_after or 0)
            else:
                if feed is None:
                    feeds.pop(kind, None)
                else:
                    feeds[kind] = feed
                failed.discard(kind)
                errors.pop(kind, None)
                self._retry_at.pop(kind, None)
        snapshot = self.live.data
        active = snapshot is not None and (
            self.live.view(snapshot.series_id).session_status == "active"
        )
        self.update_interval = (
            max(SCORING_INTERVAL, self.live.live_interval)
            if active
            else SCORING_IDLE_INTERVAL
        )
        result = ScoringData(feeds, frozenset(failed), errors)
        self._schedule_expiry(result)
        return result
