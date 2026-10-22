"""Test-only actual HA runtime, installed from the self-contained component tree.

No owner config, provider calls, custom web server or HACS network access.
Synthetic version rewrites exercise cache transitions, not unpublished releases.
"""

import argparse
import asyncio
import hashlib
import json
import shutil
import signal
import tempfile
from contextlib import nullcontext
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

import aiohttp
from aiohttp import web
from homeassistant import bootstrap, loader, setup
from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from yarl import URL

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = "nascar_race_center"


class Harness(HomeAssistantView):
    url = "/packaging-test"
    name = "packaging-test:harness"
    requires_auth = False

    async def get(self, request):
        # Vite's test-only mock supplies synthetic dashboard data; the loader and
        # all installed card bytes are served by real HA at this same origin.
        return web.Response(
            text="""<!doctype html><html><body><script type="module">
import { MockHass } from "http://127.0.0.1:5173/demo/mock.ts";
const resource = localStorage.getItem("test-resource") || "/nascar_race_center/card.js";
await import(resource);
const config = JSON.parse(localStorage.getItem("test-card") || "null") || {
 type: "custom:nascar-race-center-card", entry_id: "FICTIONAL_ENTRY",
 section: "Live Timing"
};
const card = new (customElements.get("nascar-race-center-card"))();
const hass = new MockHass(); card.setConfig(config); card.hass = hass;
document.body.append(card); window.nrcDemo = { card, hass };
</script></body></html>""",
            content_type="text/html",
            headers={"Cache-Control": "no-store"},
        )


class EntryProbe(HomeAssistantView):
    """Test-only state of fictional entries; never part of the installed package."""

    url = "/packaging-entry-test"
    name = "packaging-test:entry"
    requires_auth = False

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        entries = self.hass.config_entries.async_entries(DOMAIN)
        if len(entries) != 1 or entries[0].state.value != "loaded":
            return web.json_response({"ready": False}, status=503)
        entry = entries[0]
        return web.json_response(
            {
                "entry_id": entry.entry_id,
                "favorites": entry.data.get("favorite_drivers"),
                "series": entry.data.get("series"),
                "entities": {
                    item.unique_id: item.entity_id
                    for item in er.async_entries_for_config_entry(
                        er.async_get(self.hass), entry.entry_id
                    )
                },
            }
        )


async def run(port: int, card_version: str, config_dir: Path | None):
    work = ROOT / "work"
    work.mkdir(exist_ok=True)
    context = (
        nullcontext(str(config_dir))
        if config_dir
        else tempfile.TemporaryDirectory(prefix="bundled-ha-", dir=work)
    )
    with context as directory:
        config = Path(directory)
        package = config / "custom_components" / DOMAIN
        if package.exists():
            shutil.rmtree(package)  # Only this test's copied runtime; HA storage stays.
        shutil.copytree(
            ROOT / "custom_components" / DOMAIN,
            package,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        manifest_path = package / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        metadata_path = package / "frontend/bundle.json"
        data = json.loads(metadata_path.read_text())
        original_version = data["card_version"]
        original_file = package / "frontend" / data["filename"]
        contents = original_file.read_bytes()
        # Serve a synthetic old manual resource as a migration fixture only.
        legacy = config / "synthetic-legacy.js"
        legacy.write_bytes(contents.replace(original_version.encode(), b"0.5.3"))
        if card_version != original_version:
            original_file.unlink()
            contents = contents.replace(
                original_version.encode(), card_version.encode()
            )
            data.update(
                card_version=card_version,
                filename=f"nascar-race-center-card-{card_version}.js",
                sha256=hashlib.sha256(contents).hexdigest(),
                integration_version="0.2.2",
            )
            manifest["version"] = data["integration_version"]
            (package / "frontend" / data["filename"]).write_bytes(contents)
            metadata_path.write_text(json.dumps(data))
            manifest_path.write_text(json.dumps(manifest))
        hass = HomeAssistant(str(config))
        loader.async_setup(hass)
        stopped = asyncio.Event()
        loop = asyncio.get_running_loop()
        for signum in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(signum, stopped.set)
        try:
            assert await bootstrap.async_from_config_dict(
                {
                    "homeassistant": {
                        "latitude": 0,
                        "longitude": 0,
                        "elevation": 0,
                        "unit_system": "metric",
                        "time_zone": "UTC",
                        "country": "US",
                        "currency": "USD",
                    },
                    "http": {"server_host": "127.0.0.1", "server_port": port},
                },
                hass,
            )
            assert await setup.async_setup_component(hass, DOMAIN, {})
            loaded = import_module("custom_components.nascar_race_center")
            assert Path(loaded.__file__).parent == package
            if config_dir is not None and not hass.config_entries.async_entries(DOMAIN):
                result = await hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": "user"},
                    data={
                        "provider": "demo",
                        "series": ["1", "2", "3"],
                        "data_use_authorized": False,
                        "live_interval": 300,
                        "favorite_drivers": ["99001", "99002"],
                    },
                )
                assert result["type"] == "create_entry"
            await hass.async_block_till_done()
            hass.http.register_view(Harness())
            hass.http.register_view(EntryProbe(hass))
            await hass.http.async_register_static_paths(
                [
                    StaticPathConfig(
                        "/local/nascar-race-center/nascar-race-center-card-0.5.3.js",
                        str(legacy),
                        False,
                    )
                ]
            )
            await hass.async_start()
            await stopped.wait()
        finally:
            await hass.async_stop(force=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18123)
    parser.add_argument("--card-version", default="0.6.1")
    parser.add_argument("--config-dir", type=Path)
    args = parser.parse_args()
    if args.config_dir is not None:
        args.config_dir = args.config_dir.resolve()
        if not args.config_dir.is_relative_to((ROOT / "work").resolve()):
            raise ValueError("Persistence test config must be inside test-owned work/")
    original_request = aiohttp.ClientSession._request

    async def local_request(session, method, url, *args, **kwargs):
        if URL(url).host not in {"127.0.0.1", "localhost", "::1"}:
            raise AssertionError("Packaging runtime attempted external HTTP")
        return await original_request(session, method, url, *args, **kwargs)

    with patch.object(aiohttp.ClientSession, "_request", local_request):
        asyncio.run(run(args.port, args.card_version, args.config_dir))
