"""Entry-owned dashboard resources; HA owns authentication, transport and queues."""

import asyncio
import json
from collections import OrderedDict, deque
from collections.abc import Callable, Iterator
from time import monotonic
from typing import TYPE_CHECKING, Any

from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.core import HomeAssistant, callback

from .analytics_models import AnalyticsQuery, AnalyticsResult
from .dashboard_pages import MAX_RESPONSE_BYTES, PageError, record_page
from .dashboard_schema import fields, project
from .dashboard_snapshots import STORE_KEY, SnapshotLease, SnapshotStore, build_index
from .dashboard_views import bootstrap, live, race_summary
from .history_models import HistoricalRaceKey, HistoryDataset, HistoryResponse

if TYPE_CHECKING:
    from . import NascarConfigEntry

API_VERSION = 1
MAX_SUBSCRIPTIONS = 64
MAX_CONNECTION_SUBSCRIPTIONS = 4
MAX_REQUESTS = 8
MAX_USER_REQUESTS = 2
COALESCE_SECONDS = 0.1


def authorized(connection: ActiveConnection) -> bool:
    """Fail closed: full datasets have no HA entity/config-entry read ACL."""
    return connection.user.is_active and connection.user.is_admin


def bounded(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(payload, ensure_ascii=True, allow_nan=False).encode()
    if len(encoded) > MAX_RESPONSE_BYTES:
        raise PageError("response_too_large")
    return payload


class DashboardRuntime:
    """Entry-owned requests and subscriptions, with globally bounded snapshot slots."""

    def __init__(self, hass: HomeAssistant, entry: NascarConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.closed = False
        if STORE_KEY not in hass.data:
            hass.data[STORE_KEY] = SnapshotStore(hass.loop)
        self.snapshots: SnapshotStore = hass.data[STORE_KEY]
        self.subscriptions: dict[tuple[ActiveConnection, int], Callable[[], None]] = {}
        self.requests: dict[asyncio.Task[Any], str] = {}
        self.rates: OrderedDict[str, deque[float]] = OrderedDict()

    def admit(self, connection: ActiveConnection) -> str | None:
        """Per-user sliding window applies across tabs; bounded retained identities."""
        user_id = connection.user.id
        now = monotonic()
        times = self.rates.setdefault(user_id, deque())
        self.rates.move_to_end(user_id)
        while len(self.rates) > 128:
            self.rates.popitem(last=False)
        while times and times[0] <= now - 10:
            times.popleft()
        if len(times) >= 30:
            return "rate_limited"
        times.append(now)
        if self.closed:
            return "entry_unavailable"
        return None

    def envelope(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "api_version": API_VERSION,
            "entry_id": self.entry.entry_id,
            "data": data,
        }

    @callback
    def subscribe(self, connection: ActiveConnection, msg: dict[str, Any]) -> None:
        key = (connection, msg["id"])
        if (
            len(self.subscriptions) >= MAX_SUBSCRIPTIONS
            or sum(c is connection for c, _ in self.subscriptions)
            >= MAX_CONNECTION_SUBSCRIPTIONS
        ):
            connection.send_error(
                msg["id"], "subscription_limit", "Dashboard subscription limit reached"
            )
            return
        timer: asyncio.TimerHandle | None = None
        last: str | None = None
        revision = 0
        stopped = False
        removers: list[Callable[[], None]] = []

        @callback
        def close() -> None:
            nonlocal stopped, timer
            stopped = True
            if timer:
                timer.cancel()
                timer = None
            for remove in removers:
                remove()
            removers.clear()
            self.subscriptions.pop(key, None)

        @callback
        def emit() -> None:
            nonlocal last, timer, revision
            timer = None
            if stopped or self.closed:
                return
            if not authorized(connection):
                connection.send_error(
                    msg["id"], "unauthorized", "Administrator access required"
                )
                close()
                connection.subscriptions.pop(msg["id"], None)
                return
            try:
                data = live(self.entry, msg["series_id"])
                fingerprint = json.dumps(data, sort_keys=True, allow_nan=False)
                if fingerprint == last:
                    return
                payload = bounded(self.envelope({"revision": revision + 1, **data}))
            except ValueError:
                connection.send_error(
                    msg["id"],
                    "response_too_large",
                    "Live payload exceeds the dashboard budget",
                )
                close()
                connection.subscriptions.pop(msg["id"], None)
                return
            last = fingerprint
            revision += 1
            connection.send_event(msg["id"], payload)

        @callback
        def changed() -> None:
            nonlocal timer
            if not stopped and timer is None:
                timer = self.hass.loop.call_later(COALESCE_SECONDS, emit)

        runtime = self.entry.runtime_data
        for coordinator in (runtime.live, runtime.scoring, runtime.schedule):
            removers.append(coordinator.async_add_listener(changed))
        self.subscriptions[key] = close
        connection.subscriptions[msg["id"]] = close
        connection.send_result(msg["id"])
        emit()

    @callback
    def request(self, connection: ActiveConnection, msg: dict[str, Any]) -> None:
        user_id = connection.user.id
        if (
            len(self.requests) >= MAX_REQUESTS
            or sum(u == user_id for u in self.requests.values()) >= MAX_USER_REQUESTS
        ):
            connection.send_error(
                msg["id"],
                "request_limit",
                "Dashboard request budget reached; retry after work completes",
            )
            return
        task = self.hass.async_create_background_task(
            self._request(connection, msg),
            "NASCAR dashboard request",
            eager_start=False,
        )
        self.requests[task] = user_id
        connection.subscriptions[("nascar_dashboard_request", msg["id"])] = task.cancel

    async def _request(self, connection: ActiveConnection, msg: dict[str, Any]) -> None:
        task = asyncio.current_task()
        try:
            data = await self._data(msg, connection)
            if not self.closed and authorized(connection):
                # Measure and serialize bounded responses outside the event loop.
                payload = await self._executor(bounded, self.envelope(data))
                if not self.closed and authorized(connection):
                    connection.send_result(msg["id"], payload)
            elif not self.closed:
                connection.send_error(
                    msg["id"], "unauthorized", "Administrator access required"
                )
        except PageError as err:
            connection.send_error(
                msg["id"],
                str(err),
                "Dashboard page unavailable; restart selection if the snapshot changed",
            )
        except ValueError:
            connection.send_error(
                msg["id"], "invalid_selection", "Invalid dashboard selection"
            )
        except RuntimeError:
            connection.send_error(
                msg["id"], "entry_unavailable", "Configuration entry is unavailable"
            )
        finally:
            if task is not None:
                self.requests.pop(task, None)
            connection.subscriptions.pop(("nascar_dashboard_request", msg["id"]), None)

    async def _executor[T](self, target: Callable[..., T], *args: Any) -> T:
        """Keep a cancelled serializer's slot until its bounded worker drains."""
        future = self.hass.async_add_executor_job(target, *args)
        cancelled = False
        while True:
            try:
                result = await asyncio.shield(future)
                break
            except asyncio.CancelledError:
                if future.cancelled():
                    raise
                cancelled = True
        if cancelled:
            raise asyncio.CancelledError
        return result

    async def _data(
        self, msg: dict[str, Any], connection: ActiveConnection
    ) -> dict[str, Any]:
        runtime = self.entry.runtime_data
        command = msg["type"].rsplit("/", 1)[-1]
        offset, limit, snapshot = (
            msg.get("offset", 0),
            msg.get("limit", 100),
            msg.get("snapshot"),
        )
        if offset and not snapshot:
            raise PageError("snapshot_required")
        if command == "bootstrap":
            return bootstrap(self.entry)
        if command == "live":
            return live(self.entry, msg["series_id"])
        if command == "schedule":
            series = msg["series_id"]
            races = runtime.schedule.usable_races(series)

            def schedule_records() -> Iterator[dict[str, Any]]:
                for race in races:
                    if (
                        "season" in msg
                        and race.season != msg["season"]
                        or "race_id" in msg
                        and race.race_id != msg["race_id"]
                    ):
                        continue
                    yield {"kind": "race", "value": race_summary(race)}
                    for session in race.sessions:
                        yield {
                            "kind": "session",
                            "race_id": str(race.race_id),
                            "season": race.season,
                            "value": project(session),
                        }

            header = {
                "series_id": series,
                "seasons": sorted({r.season for r in races if r.season is not None}),
                "availability": "unavailable"
                if series in runtime.schedule.data.failed_series
                or not runtime.schedule.last_update_success
                else "available",
                "failed_seasons": sorted(
                    runtime.schedule.data.failed_seasons.get(series, ())
                ),
                "catalog_scope": "retained_supported_schedules",
                "updated_at": project(runtime.schedule.data.updated_at.get(series)),
            }
            return await self._executor(
                record_page,
                header,
                schedule_records(),
                offset,
                limit,
                snapshot,
                [series, msg.get("season"), msg.get("race_id")],
            )
        if command in ("live_driver", "live_scoring"):
            view = runtime.live.view(msg["series_id"])
            header = {
                "identity": fields(
                    view.snapshot, "series_id race_id run_id source_updated_at"
                )
                if view.snapshot
                else None,
                "availability": view.health,
            }
            if command == "live_driver":
                driver = view.driver(msg["driver_id"])
                values = getattr(driver, msg["collection"]) if driver else None
                header.update(
                    {
                        "driver_id": str(msg["driver_id"]),
                        "collection": msg["collection"],
                        "reason": None
                        if values is not None
                        else "not_reported_or_unavailable",
                    }
                )
            else:
                feed = runtime.scoring.feed(msg["collection"], msg["series_id"])
                values = getattr(feed, msg["collection"]) if feed else None
                header.update(
                    {
                        "collection": msg["collection"],
                        "availability": runtime.scoring.capability(
                            msg["collection"], msg["series_id"]
                        ),
                        "provenance": project(feed.provenance) if feed else None,
                    }
                )
            return await self._executor(
                record_page,
                header,
                ({"value": project(v)} for v in values or ()),
                offset,
                limit,
                snapshot,
                header,
            )
        # Bind to validated command/entry/race/datasets and all analytics options.
        # Paging controls may vary; dataset order is part of the ordered stream.
        selection = json.dumps(
            {
                k: v
                for k, v in msg.items()
                if k not in ("id", "offset", "limit", "snapshot")
            },
            sort_keys=True,
        )
        if snapshot is not None:
            lease = self.snapshots.get(snapshot, self, connection, selection)
            try:
                assert lease.index is not None
                return await self._executor(lease.index.page, snapshot, offset, limit)
            finally:
                self.snapshots.finish_read(lease)
        lease = self.snapshots.reserve(self, connection, selection)
        try:
            return await self._snapshot_data(msg, lease, offset, limit)
        except BaseException:
            self.snapshots.release(lease)
            raise

    async def _snapshot_data(
        self, msg: dict[str, Any], lease: SnapshotLease, offset: int, limit: int
    ) -> dict[str, Any]:
        runtime = self.entry.runtime_data
        command = msg["type"].rsplit("/", 1)[-1]
        key = HistoricalRaceKey(msg["season"], msg["series_id"], msg["race_id"])
        datasets = tuple(HistoryDataset(d) for d in msg["datasets"])
        result: HistoryResponse | AnalyticsResult
        if command == "history":
            result = await runtime.history.async_get(key, datasets)
        else:
            query = AnalyticsQuery(
                key,
                tuple(msg["driver_ids"]),
                msg["first_lap"],
                msg["last_lap"],
                tuple(msg["windows"]),
                msg["time_basis"],
            )
            result = await runtime.analytics.async_get(query, datasets)
        index = await self._executor(build_index, result)
        self.snapshots.publish(lease, index)
        lease.readers += 1
        try:
            return await self._executor(index.page, lease.token, offset, limit)
        finally:
            self.snapshots.finish_read(lease)

    async def async_close(self, _: object = None) -> None:
        """Unload/reload/shutdown closes sockets' entry work without touching peers."""
        self.closed = True
        for (connection, msg_id), close in tuple(self.subscriptions.items()):
            connection.send_event(
                msg_id,
                self.envelope(
                    {"availability": "entry_unavailable", "reason": "entry_unloaded"}
                ),
            )
            close()
            connection.subscriptions.pop(msg_id, None)
        tasks = tuple(self.requests)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.snapshots.close(self)
        self.rates.clear()
