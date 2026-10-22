"""Serve bundled public code through HA; never register or edit Lovelace resources."""

import asyncio
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from aiohttp import web

# Documented public HA exports; its stubs omit explicit re-export aliases.
from homeassistant.components.http import (  # type: ignore[attr-defined]
    HomeAssistantView,
    StaticPathConfig,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
DATA_KEY = f"{DOMAIN}_frontend"
PACKAGE_DIR = Path(__file__).parent
RESOURCE_URL = f"/{DOMAIN}/card.js"


@dataclass(frozen=True, slots=True)
class Bundle:
    """Build-pinned identity; no provider or user data."""

    integration_version: str
    card_version: str
    filename: str
    sha256: str

    @property
    def url(self) -> str:
        return f"/{DOMAIN}/{self.filename}?v={self.sha256}"

    @property
    def loader(self) -> str:
        # Module identity is canonical even when the resource has query aliases.
        # An already loaded card requires a document reload, never redefinition.
        return (
            'if (!customElements.get("nascar-race-center-card")) {\n'
            f"  await import({json.dumps(self.url)});\n"
            "}\n"
        )


def read_bundle(package: Path) -> Bundle:
    """Validate the entire immutable artifact in an executor before exposing it."""
    with (package / "frontend" / "bundle.json").open("rb") as handle:
        metadata = handle.read(4097)
    with (package / "manifest.json").open("rb") as handle:
        manifest = handle.read(8193)
    if len(metadata) > 4096 or len(manifest) > 8192:
        raise ValueError("Oversize bundled card metadata")
    data = json.loads(metadata)
    version = json.loads(manifest)["version"]
    if not isinstance(data, dict) or set(data) != {
        "integration_version",
        "card_version",
        "filename",
        "sha256",
    }:
        raise ValueError("Invalid bundled card metadata")
    if not all(isinstance(value, str) for value in data.values()):
        raise ValueError("Invalid bundled card metadata types")
    bundle = Bundle(**data)
    if (
        bundle.integration_version != version
        or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", bundle.card_version) is None
        or bundle.filename != f"nascar-race-center-card-{bundle.card_version}.js"
        or re.fullmatch(r"[0-9a-f]{64}", bundle.sha256) is None
    ):
        raise ValueError("Incompatible bundled card identity")
    target = package / "frontend" / bundle.filename
    with target.open("rb") as handle:
        contents = handle.read(180001)
    if (
        len(contents) > 180000
        or target.is_symlink()
        or hashlib.sha256(contents).hexdigest() != bundle.sha256
    ):
        raise ValueError("Bundled card checksum mismatch")
    return bundle


@dataclass(slots=True)
class FrontendState:
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    registered: bool = False
    bundle: Bundle | None = None
    error: bool = False


class CardLoaderView(HomeAssistantView):
    """A small generated module, with explicit cache policy and no filesystem I/O."""

    url = RESOURCE_URL
    name = f"{DOMAIN}:card_loader"
    requires_auth = False

    def __init__(self, bundle: Bundle | None) -> None:
        self.bundle = bundle

    async def get(self, request: web.Request) -> web.Response:
        return web.Response(
            text=self.bundle.loader
            if self.bundle
            else (
                "Bundled card unavailable; restore the complete integration "
                "and restart Home Assistant."
            ),
            content_type="application/javascript" if self.bundle else "text/plain",
            status=200 if self.bundle else 503,
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )


async def async_setup_frontend(hass: HomeAssistant) -> None:
    """Register once per HA process, independent of entries and their reloads."""
    state: FrontendState = hass.data.setdefault(DATA_KEY, FrontendState())
    async with state.lock:
        if state.registered:
            return
        try:
            bundle = await hass.async_add_executor_job(read_bundle, PACKAGE_DIR)
        except OSError, ValueError, KeyError, TypeError:
            # Optional frontend damage must not disable schedules or automations.
            state.error = True
            _LOGGER.error(
                "Bundled card validation failed; restore the complete integration "
                "and restart Home Assistant"
            )
            bundle = None
        if bundle:
            await hass.http.async_register_static_paths(
                [
                    StaticPathConfig(
                        f"/{DOMAIN}/{bundle.filename}",
                        str(PACKAGE_DIR / "frontend" / bundle.filename),
                        True,
                    )
                ]
            )
        hass.http.register_view(CardLoaderView(bundle))
        state.bundle = bundle
        state.registered = True


def packaging_diagnostics(hass: HomeAssistant) -> dict[str, object]:
    """Report exact loaded build identity, without local paths or user settings."""
    state = hass.data.get(DATA_KEY)
    bundle = state.bundle if isinstance(state, FrontendState) else None
    return {
        "status": "available" if bundle else "unavailable",
        "resource_url": RESOURCE_URL,
        "resource_registration": "one_time_manual",
        "integration_version": bundle.integration_version if bundle else None,
        "card_version": bundle.card_version if bundle else None,
        "sha256": bundle.sha256 if bundle else None,
        "module_url": bundle.url if bundle else None,
        "update_requires": "core_restart_and_browser_document_reload",
    }
