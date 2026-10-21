"""A compact CF live-request reservation survives reload/restart, without bodies."""

from datetime import datetime, timedelta
from pathlib import Path

from homeassistant.core import CoreState, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .models import ProviderError


class LiveRequestGuard:
    """Reserve before I/O; storage failure disables live I/O for this load.

    This retains only one next-eligible UTC deadline, not source data or history.
    Reload never clears a server cooldown or an already reserved request slot.
    """

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self.hass = hass
        self.store: Store[dict[str, str]] = Store(
            hass, 1, f"{DOMAIN}.{entry_id}.live_polling", private=True
        )
        self.deadline: datetime | None = None
        self.host_deadline: datetime | None = None
        self.failed = False

    async def async_load(self) -> None:
        try:
            path = Path(self.store.path)
            existed = await self.hass.async_add_executor_job(
                lambda: path.exists() or any(path.parent.glob(f"{path.name}.corrupt.*"))
            )
            data = await self.store.async_load()
            if data is not None:
                deadline = datetime.fromisoformat(data["not_before"])
                if deadline.utcoffset() is None:
                    raise ValueError("Unknown request reservation timezone")
                host_deadline = None
                if value := data.get("host_not_before"):
                    host_deadline = datetime.fromisoformat(value)
                    if host_deadline.utcoffset() is None:
                        raise ValueError("Unknown host cooldown timezone")
                self.deadline = deadline
                self.host_deadline = host_deadline
            elif existed:
                raise ValueError("Invalid request reservation")
        except OSError, ValueError, TypeError, KeyError, HomeAssistantError:
            self.failed = True

    @property
    def host_remaining(self) -> float:
        return (
            max(0, (self.host_deadline - dt_util.utcnow()).total_seconds())
            if self.host_deadline
            else 0
        )

    @property
    def remaining(self) -> float:
        if self.failed:
            return 21600
        return (
            max(0, (self.deadline - dt_util.utcnow()).total_seconds())
            if self.deadline
            else 0
        )

    async def async_reserve(self, seconds: float, *, hostwide: bool = False) -> None:
        """Verify HA Store's write-back before allowing another network attempt."""
        if self.failed:
            raise ProviderError(
                "Live polling reservation unavailable", retry_after=21600
            )
        try:
            if self.hass.state in {
                CoreState.stopping,
                CoreState.final_write,
                CoreState.stopped,
            }:
                raise ValueError("HA is stopping")
            deadline = dt_util.utcnow() + timedelta(seconds=seconds)
            host_deadline = self.host_deadline
            if hostwide:
                host_deadline = max(deadline, host_deadline or deadline)
            deadline = max(deadline, self.deadline or deadline)
            if self.deadline == deadline and self.host_deadline == host_deadline:
                return
            data = {"not_before": deadline.isoformat()}
            if host_deadline is not None:
                data["host_not_before"] = host_deadline.isoformat()
            await self.store.async_save(data)
            if self.hass.state in {
                CoreState.stopping,
                CoreState.final_write,
                CoreState.stopped,
            }:
                raise ValueError("HA stopped before request reservation")
            if await self.store.async_load() != data:
                raise ValueError("Request reservation did not persist")
            self.deadline = deadline
            self.host_deadline = host_deadline
        except OSError, ValueError, OverflowError, HomeAssistantError:
            self.failed = True
            raise ProviderError(
                "Live polling reservation unavailable", retry_after=21600
            ) from None
