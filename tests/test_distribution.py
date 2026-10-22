"""Offline HACS-layout archive contracts, independent of a public GitHub service."""

import hashlib
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from build_distribution import ROOT, build


def test_preview_is_deterministic_complete_and_does_not_ship_development_data(tmp_path):
    first = build(tmp_path / "first", "example/nrc-distribution")
    second = build(tmp_path / "second", "example/nrc-distribution")
    assert first.read_bytes() == second.read_bytes()
    with ZipFile(first) as archive:
        names = archive.namelist()
        assert names == sorted(names)
        assert not any(
            name.startswith(("work/", "tests/", ".git/", "frontend/", "docs/nascar"))
            for name in names
        )
        components = {
            name.split("/")[1]
            for name in names
            if name.startswith("custom_components/")
        }
        assert components == {"nascar_race_center"}
        prefix = "custom_components/nascar_race_center/"
        manifest = json.loads(archive.read(prefix + "manifest.json"))
        assert (
            manifest["documentation"] == "https://github.com/example/nrc-distribution"
        )
        assert (
            manifest["issue_tracker"]
            == "https://github.com/example/nrc-distribution/issues"
        )
        assert manifest["domain"] == "nascar_race_center"
        metadata = json.loads(archive.read(prefix + "frontend/bundle.json"))
        assert (
            hashlib.sha256(
                archive.read(prefix + "frontend/" + metadata["filename"])
            ).hexdigest()
            == metadata["sha256"]
        )
        for line in archive.read("SHA256SUMS").decode().splitlines():
            digest, name = line.split("  ", 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
        assert not json.loads(archive.read("DISTRIBUTION.json"))["published"]
        upgrade = archive.read("REAL_CF_UPGRADE.md").decode()
        assert "(UPGRADE.md)" in upgrade
        assert "(HACS_MIGRATION.md)" not in upgrade
        assert "(REAL_CF_ARTIFACTS.sha256)" in upgrade
        assert "(REAL_CF_UPGRADE.md)" in archive.read("UPGRADE.md").decode()
        assert archive.read("REAL_CF_ARTIFACTS.sha256")
        # A normal integration download/extraction contains all runtime assets.
        installed = tmp_path / "config"
        archive.extractall(installed)
        assert (installed / prefix / "frontend" / metadata["filename"]).is_file()
        assert (installed / prefix / "brand/icon.png").is_file()
    with pytest.raises(FileExistsError):
        build(tmp_path / "first", "example/nrc-distribution")


@pytest.mark.parametrize("damage", ["extra", "symlink", "checksum"])
def test_export_rejects_unreviewed_or_damaged_runtime_before_writing(tmp_path, damage):
    root = tmp_path / "source"
    source = root / "custom_components/nascar_race_center"
    shutil.copytree(
        ROOT / "custom_components/nascar_race_center",
        source,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    if damage == "extra":
        (source / "credentials.txt").write_text("synthetic forbidden file")
    if damage == "symlink":
        (source / "unexpected.py").symlink_to(source / "__init__.py")
    if damage == "checksum":
        meta = json.loads((source / "frontend/bundle.json").read_text())
        (source / "frontend" / meta["filename"]).write_text("broken")
    target = tmp_path / "preview"
    with pytest.raises(ValueError):
        build(target, "example/nrc-distribution", root=root)
    assert not target.exists()


def test_invalid_destination_cannot_enter_manifest_or_paths(tmp_path):
    for name in [
        "../escape",
        "owner/repo/other",
        "https://github.com/owner/repo",
        "owner/repo;command",
    ]:
        with pytest.raises(ValueError):
            build(tmp_path / "out", name)
    assert not (tmp_path / "out").exists()
