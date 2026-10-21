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
                self.deadline = deadline
            elif existed:
                raise ValueError("Invalid request reservation")
        except OSError, ValueError, TypeError, KeyError, HomeAssistantError:
            self.failed = True

    @property
    def remaining(self) -> float:
        if self.failed:
            return 21600
        return (
            max(0, (self.deadline - dt_util.utcnow()).total_seconds())
            if self.deadline
            else 0
        )

    async def async_reserve(self, seconds: float) -> None:
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
            if self.deadline is not None and self.deadline >= deadline:
                return
            data = {"not_before": deadline.isoformat()}
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
        except OSError, ValueError, OverflowError, HomeAssistantError:
            self.failed = True
            raise ProviderError(
                "Live polling reservation unavailable", retry_after=21600
            ) from None
