"""Export/import framework packages for GitHub Releases."""

from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Any

from cursor_loop_runtime.models import sha256_file, utcnow, write_json_atomic

from .framework_core import install_into
from .versions import framework_root, read_framework_version


def export_package(output_dir: Path | None = None) -> dict[str, Any]:
    root = framework_root()
    version = read_framework_version()
    output_dir = (output_dir or (root / "dist")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="cle-export-"))
    try:
        pkg_name = f"cursor-loop-engineering-{version}"
        pkg_root = staging / pkg_name
        pkg_root.mkdir()
        # Copy essential framework payload
        for rel in (
            "VERSION",
            "COMPATIBILITY.json",
            "LICENSE",
            "README.md",
            "MARKETPLACE.md",
            "mcp.json",
            ".cursor-plugin",
            ".cursor",
            "rules",
            "skills",
            "agents",
            "commands",
            "hooks",
            "templates",
            "examples",
            "assets",
            "migration",
            "install",
            "runtime",
            "sdk",
            "scripts",
            "docs",
            "pyproject.toml",
        ):
            src = root / rel
            if not src.exists():
                continue
            dest = pkg_root / rel
            if src.is_dir():
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "*.egg-info"))
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        meta = {
            "framework": "cursor-loop-engineering",
            "version": version,
            "exported_at": utcnow(),
            "contents": sorted(p.name for p in pkg_root.iterdir()),
        }
        write_json_atomic(pkg_root / "package.json", meta)
        archive = output_dir / f"{pkg_name}.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(pkg_root, arcname=pkg_name)
        checksum = sha256_file(archive)
        checksum_path = output_dir / f"{pkg_name}.sha256"
        checksum_path.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
        return {
            "result": "PASS",
            "version": version,
            "archive": str(archive),
            "sha256": checksum,
            "checksum_file": str(checksum_path),
            "exported_at": utcnow(),
        }
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def import_package(archive: Path, target: Path, *, force: bool = False) -> dict[str, Any]:
    archive = archive.resolve()
    target = target.resolve()
    if not archive.exists():
        raise FileNotFoundError(f"archive not found: {archive}")
    extract_root = Path(tempfile.mkdtemp(prefix="cle-import-"))
    try:
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(extract_root)
        children = [p for p in extract_root.iterdir() if p.is_dir()]
        if not children:
            raise RuntimeError("archive contains no package directory")
        package_root = children[0]
        # Temporarily treat package as framework root by installing assets from it
        result = install_into(target, force=force, source_root=package_root)
        result["imported_from"] = str(archive)
        result["package_root"] = str(package_root)
        pkg_meta = package_root / "package.json"
        if pkg_meta.exists():
            result["package"] = json.loads(pkg_meta.read_text(encoding="utf-8"))
        return result
    finally:
        shutil.rmtree(extract_root, ignore_errors=True)
