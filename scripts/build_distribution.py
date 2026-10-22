"""Create a deterministic, local-only distribution preview. Never publish anything."""

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "nascar_race_center"


def checked_files(root: Path) -> list[Path]:
    """Fail closed on unexpected files, symlinks and extra bundled modules."""
    metadata = json.loads((root / "frontend/bundle.json").read_text())
    manifest = json.loads((root / "manifest.json").read_text())
    name = metadata["filename"]
    version = metadata["card_version"]
    if (
        re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None
        or name != f"nascar-race-center-card-{version}.js"
        or manifest["version"] != metadata["integration_version"]
        or hashlib.sha256((root / "frontend" / name).read_bytes()).hexdigest()
        != metadata["sha256"]
    ):
        raise ValueError("Incompatible or damaged distribution bundle")
    exact = {
        "manifest.json",
        "strings.json",
        "translations/en.json",
        "brand/icon.png",
        "brand/icon.svg",
        "brand/README.md",
        "frontend/bundle.json",
        f"frontend/{name}",
        "frontend/LICENSE",
        "frontend/THIRD_PARTY_NOTICES.md",
    }
    files = []
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            raise ValueError("Distribution must not contain symlinks")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if not (relative in exact or path.parent == root and path.suffix == ".py"):
            raise ValueError(f"Unexpected distribution file: {relative}")
        files.append(path)
    if not all((root / path).is_file() for path in exact):
        raise ValueError("Required distribution file is missing")
    return files


def build(output: Path, repository: str, *, root: Path = ROOT) -> Path:
    """Export only reviewed runtime/license/docs; do not overwrite any directory."""
    if (
        re.fullmatch(
            r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}",
            repository,
        )
        is None
    ):
        raise ValueError("Specify a GitHub repository as owner/name")
    source = root / "custom_components" / DOMAIN
    files = checked_files(source)
    # Exclusive creation prevents accidental replacement of previous previews.
    output.mkdir(parents=True, exist_ok=False)
    tree = output / "repository"
    destination = tree / "custom_components" / DOMAIN
    for path in files:
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    for name in ("LICENSE", "hacs.json"):
        shutil.copyfile(root / name, tree / name)
    workflows = tree / ".github/workflows"
    workflows.mkdir(parents=True)
    shutil.copyfile(root / ".github/workflows/validate.yml", workflows / "validate.yml")
    for source_name, target_name in (
        ("DISTRIBUTION_README.md", "README.md"),
        ("HACS_MIGRATION.md", "UPGRADE.md"),
        ("REAL_CF_UPGRADE.md", "REAL_CF_UPGRADE.md"),
        ("REAL_CF_ARTIFACTS.sha256", "REAL_CF_ARTIFACTS.sha256"),
        ("DATA_USE.md", "DATA_USE.md"),
    ):
        shutil.copyfile(root / "docs" / source_name, tree / target_name)
    upgrade_path = tree / "REAL_CF_UPGRADE.md"
    upgrade_path.write_text(
        upgrade_path.read_text().replace("(HACS_MIGRATION.md)", "(UPGRADE.md)")
    )
    manifest_path = destination / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(
        documentation=f"https://github.com/{repository}",
        issue_tracker=f"https://github.com/{repository}/issues",
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    metadata = json.loads((destination / "frontend/bundle.json").read_text())
    (tree / "DISTRIBUTION.json").write_text(
        json.dumps(
            {
                "repository": repository,
                "tag": f"v{manifest['version']}",
                "integration_version": manifest["version"],
                "card_version": metadata["card_version"],
                "card_sha256": metadata["sha256"],
                "published": False,
            },
            indent=2,
        )
        + "\n"
    )
    members = sorted(
        (path for path in tree.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(tree).as_posix(),
    )
    sums = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
        f"{path.relative_to(tree).as_posix()}\n"
        for path in members
    )
    (tree / "SHA256SUMS").write_text(sums)
    archive = output / f"nascar-race-center-{manifest['version']}.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as zipped:
        for path in sorted(
            tree.rglob("*"), key=lambda path: path.relative_to(tree).as_posix()
        ):
            if path.is_file():
                info = ZipInfo(
                    path.relative_to(tree).as_posix(), date_time=(1980, 1, 1, 0, 0, 0)
                )
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                zipped.writestr(info, path.read_bytes(), compresslevel=9)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "ARCHIVE.sha256").write_text(f"{digest}  {archive.name}\n")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--repository",
        required=True,
        help="Owner-approved future destination; no network operation is performed",
    )
    args = parser.parse_args()
    artifact = build(args.output, args.repository)
    print(f"Local preview only: {artifact}")
    print((args.output / "ARCHIVE.sha256").read_text(), end="")
