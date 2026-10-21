"""Process-bounded ephemeral serialized cursors; never retain raw feed bodies."""

import asyncio
import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256
from sys import getsizeof
from typing import Any

from homeassistant.components.websocket_api.connection import ActiveConnection

from .analytics_models import AnalyticsResult
from .dashboard_pages import MAX_RESPONSE_BYTES, PageError, result_records
from .history_models import HistoryResponse

STORE_KEY = "nascar_race_center.dashboard_snapshots"
MAX_SNAPSHOTS = 4  # Across every entry/user, including workers under construction.
MAX_USER_SNAPSHOTS = 2
MAX_SNAPSHOT_BYTES = 24 * 1024 * 1024
MAX_SNAPSHOT_RECORDS = 100_000
SNAPSHOT_SECONDS = 300


@dataclass(frozen=True, slots=True)
class SnapshotIndex:
    header: bytes
    rows: tuple[bytes, ...]
    content_version: str
    retained_bytes: int

    def page(self, token: str, offset: int, limit: int) -> dict[str, Any]:
        if offset > len(self.rows):
            raise PageError("invalid_offset")
        rows = []
        used = len(self.header) + 2048
        for encoded in self.rows[offset : offset + limit]:
            if used + len(encoded) + 2 > MAX_RESPONSE_BYTES:
                break
            rows.append(json.loads(encoded))
            used += len(encoded) + 2
        end = offset + len(rows)
        return {
            **json.loads(self.header),
            "records": rows,
            "pagination": {
                "offset": offset,
                "limit": limit,
                "returned": len(rows),
                "total": len(self.rows),
                "next_offset": end if end < len(self.rows) else None,
                "snapshot": token,
                "complete": end == len(self.rows),
            },
        }


def build_index(result: HistoryResponse | AnalyticsResult) -> SnapshotIndex:
    """One projection/hash pass; reject every unpageable row before issuing a token.

    Budget includes bytes object overhead and conservative list/tuple pointers.
    The caller reserves a full slot before retrieval and holds it through drain.
    Only encoded allowlisted normalized projections survive this function.
    """
    header, records, context = result_records(result)
    encoded_header = json.dumps(header, ensure_ascii=True, allow_nan=False).encode()
    digest = sha256(json.dumps(context, allow_nan=False).encode())
    digest.update(encoded_header)
    used = getsizeof(encoded_header) + 8192
    if len(encoded_header) + 2048 >= MAX_RESPONSE_BYTES:
        raise PageError("response_too_large")
    rows: list[bytes] = []
    for record in records:
        encoded = json.dumps(record, ensure_ascii=True, allow_nan=False).encode()
        if len(encoded_header) + len(encoded) + 2050 > MAX_RESPONSE_BYTES:
            raise PageError("record_too_large")
        used += getsizeof(encoded) + 24
        if used > MAX_SNAPSHOT_BYTES or len(rows) >= MAX_SNAPSHOT_RECORDS:
            raise PageError("snapshot_too_large")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        rows.append(encoded)
    return SnapshotIndex(encoded_header, tuple(rows), digest.hexdigest(), used)


@dataclass(slots=True)
class SnapshotLease:
    owner: object
    connection: ActiveConnection
    selection: str
    user_id: str
    token: str
    index: SnapshotIndex | None = None
    expires: float = 0
    timer: asyncio.TimerHandle | None = None


class SnapshotStore:
    """HA-instance-wide budget: four reserved 24 MiB slots, fixed five-minute TTL."""

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self.leases: dict[str, SnapshotLease] = {}

    def reserve(
        self, owner: object, connection: ActiveConnection, selection: str
    ) -> SnapshotLease:
        if (
            len(self.leases) >= MAX_SNAPSHOTS
            or sum(
                lease.user_id == connection.user.id for lease in self.leases.values()
            )
            >= MAX_USER_SNAPSHOTS
        ):
            raise PageError("snapshot_limit")
        lease = SnapshotLease(
            owner, connection, selection, connection.user.id, secrets.token_hex(32)
        )
        self.leases[lease.token] = lease
        return lease

    def publish(self, lease: SnapshotLease, index: SnapshotIndex) -> None:
        # Opaque random identity also incorporates the immutable content version.
        self.leases.pop(lease.token)
        lease.token = sha256(
            (lease.token + lease.selection + index.content_version).encode()
        ).hexdigest()
        lease.index = index
        lease.expires = self.loop.time() + SNAPSHOT_SECONDS
        self.leases[lease.token] = lease
        lease.timer = self.loop.call_later(SNAPSHOT_SECONDS, self.release, lease)
        lease.connection.subscriptions[(STORE_KEY, lease.token)] = self.cleanup(lease)

    def cleanup(self, lease: SnapshotLease) -> Callable[[], None]:
        return lambda: self.release(lease, remove_subscription=False)

    def release(
        self, lease: SnapshotLease, *, remove_subscription: bool = True
    ) -> None:
        self.leases.pop(lease.token, None)
        if remove_subscription:
            lease.connection.subscriptions.pop((STORE_KEY, lease.token), None)
        if lease.timer is not None:
            lease.timer.cancel()
        lease.index = None

    def get(
        self, token: str, owner: object, connection: ActiveConnection, selection: str
    ) -> SnapshotIndex:
        lease = self.leases.get(token)
        if (
            lease is None
            or lease.owner is not owner
            or lease.connection is not connection
            or lease.user_id != connection.user.id
            or lease.selection != selection
            or lease.index is None
        ):
            raise PageError("snapshot_invalid")
        if self.loop.time() >= lease.expires:
            self.release(lease)
            raise PageError("snapshot_expired")
        return lease.index

    def close(self, owner: object) -> None:
        for lease in tuple(self.leases.values()):
            if lease.owner is owner:
                self.release(lease)
