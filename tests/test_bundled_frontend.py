"""Actual HA HTTP and config-entry lifecycle over the installed public bundle."""

import asyncio
import hashlib
import json
import re
import shutil

import pytest
from homeassistant.helpers import entity_registry as er
from test_beta_smoke import loopback_only_http as loopback_only_http
from test_init import demo_entry

from custom_components.nascar_race_center import frontend
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)

pytestmark = pytest.mark.usefixtures("socket_enabled", "loopback_only_http")


@pytest.fixture
async def bundled_entry(hass):
    entry = demo_entry(["1", "2", "3"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_public_code_exact_bytes_no_store_loader_and_private_source(
    hass, bundled_entry, aiohttp_client
):
    client = await aiohttp_client(hass.http.app)
    response = await client.get(frontend.RESOURCE_URL)
    assert response.status == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert "ETag" not in response.headers
    assert response.content_type == "application/javascript"
    loader = await response.text()
    bundle = frontend.read_bundle(frontend.PACKAGE_DIR)
    assert json.dumps(bundle.url) in loader
    response = await client.get(bundle.url)
    body = await response.read()
    assert response.status == 200
    assert hashlib.sha256(body).hexdigest() == bundle.sha256
    assert "max-age=" in response.headers["Cache-Control"]
    # A warm browser's module validation works; the loader never returns stale 304.
    headers = {"If-None-Match": response.headers["ETag"]}
    assert (await client.get(bundle.url, headers=headers)).status == 304
    assert (await client.get(frontend.RESOURCE_URL, headers=headers)).status == 200
    for path in (
        "manifest.json",
        "__init__.py",
        "frontend/bundle.json",
        "../manifest.json",
    ):
        assert (await client.get(f"/nascar_race_center/{path}")).status == 404
    diag = await async_get_config_entry_diagnostics(hass, bundled_entry)
    assert diag["packaging"]["card_version"] == bundle.card_version
    assert diag["packaging"]["sha256"] == bundle.sha256


async def test_reload_two_clients_concurrent_registration_and_remove_preserve_resources(
    hass, bundled_entry, aiohttp_client, hass_ws_client
):
    registry = er.async_get(hass)
    before = {
        e.unique_id: e.entity_id
        for e in er.async_entries_for_config_entry(registry, bundled_entry.entry_id)
    }
    first, second = [await aiohttp_client(hass.http.app) for _ in range(2)]
    routes = len(list(hass.http.app.router.routes()))
    await asyncio.gather(*(frontend.async_setup_frontend(hass) for _ in range(8)))
    assert len(list(hass.http.app.router.routes())) == routes
    # Never initialize Lovelace, add resources or touch its storage collection.
    assert "lovelace" not in hass.config.components
    ws = await hass_ws_client(hass)
    await ws.send_json_auto_id(
        {
            "type": "nascar_race_center/dashboard/bootstrap",
            "entry_id": bundled_entry.entry_id,
            "api_version": 1,
        }
    )
    assert (await ws.receive_json())["success"]
    await ws.close()
    routes = len(list(hass.http.app.router.routes()))
    assert await hass.config_entries.async_reload(bundled_entry.entry_id)
    await hass.async_block_till_done()
    after = {
        e.unique_id: e.entity_id
        for e in er.async_entries_for_config_entry(registry, bundled_entry.entry_id)
    }
    assert after == before
    assert len(list(hass.http.app.router.routes())) == routes
    assert await hass.config_entries.async_unload(bundled_entry.entry_id)
    assert (await first.get(frontend.RESOURCE_URL)).status == 200
    assert (await second.get(frontend.RESOURCE_URL)).status == 200
    # Public code persists until process restart; entry-owned data is unavailable.
    ws = await hass_ws_client(hass)
    await ws.send_json_auto_id(
        {
            "type": "nascar_race_center/dashboard/bootstrap",
            "entry_id": bundled_entry.entry_id,
            "api_version": 1,
        }
    )
    assert not (await ws.receive_json())["success"]
    await ws.close()
    assert await hass.config_entries.async_setup(bundled_entry.entry_id)
    assert {
        e.unique_id: e.entity_id
        for e in er.async_entries_for_config_entry(registry, bundled_entry.entry_id)
    } == before


@pytest.mark.parametrize(
    "failure", ["missing", "checksum", "path", "version", "oversize"]
)
async def test_damaged_optional_bundle_fails_closed_without_disabling_entities(
    hass, tmp_path, monkeypatch, aiohttp_client, failure
):
    package = tmp_path / "nascar_race_center"
    shutil.copytree(
        frontend.PACKAGE_DIR, package, ignore=shutil.ignore_patterns("__pycache__")
    )
    metadata = package / "frontend/bundle.json"
    data = json.loads(metadata.read_text())
    target = package / "frontend" / data["filename"]
    if failure == "missing":
        target.unlink()
    if failure == "checksum":
        target.write_text("unexpected changed code")
    if failure == "path":
        data["filename"] = "../manifest.json"
    if failure == "version":
        data["integration_version"] = "0.0.0"
    if failure == "oversize":
        target.write_bytes(b"x" * 180001)
    metadata.write_text(json.dumps(data))
    monkeypatch.setattr(frontend, "PACKAGE_DIR", package)
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    client = await aiohttp_client(hass.http.app)
    result = await client.get(frontend.RESOURCE_URL)
    assert result.status == 503 and result.headers["Cache-Control"] == "no-store"
    assert (await client.get(f"/nascar_race_center/{data['filename']}")).status == 404
    assert frontend.packaging_diagnostics(hass)["status"] == "unavailable"


def test_bundle_identity_and_brand_are_installed_inside_integration():
    bundle = frontend.read_bundle(frontend.PACKAGE_DIR)
    assert bundle.integration_version == "0.2.0" and bundle.card_version == "0.6.0"
    icon = (frontend.PACKAGE_DIR / "brand/icon.png").read_bytes()
    assert icon.startswith(b"\x89PNG\r\n\x1a\n")
    assert (
        int.from_bytes(icon[16:20], "big") == int.from_bytes(icon[20:24], "big") == 256
    )
    assert re.fullmatch(r"[a-f0-9]{64}", bundle.sha256)


async def test_removed_package_file_is_not_served_after_entry_unload(
    hass, tmp_path, monkeypatch, aiohttp_client
):
    package = tmp_path / "nascar_race_center"
    shutil.copytree(
        frontend.PACKAGE_DIR, package, ignore=shutil.ignore_patterns("__pycache__")
    )
    monkeypatch.setattr(frontend, "PACKAGE_DIR", package)
    entry = demo_entry(["1", "2", "3"])
    saved_data = dict(entry.data)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    client = await aiohttp_client(hass.http.app)
    bundle = frontend.read_bundle(package)
    assert (await client.get(bundle.url)).status == 200
    assert await hass.config_entries.async_unload(entry.entry_id)
    (package / "frontend" / bundle.filename).unlink()
    assert (await client.get(bundle.url)).status == 404
    # Entry configuration survives temporary disable/package removal.
    assert hass.config_entries.async_get_entry(entry.entry_id) is entry
    assert dict(entry.data) == saved_data
