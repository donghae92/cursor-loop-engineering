"""Detect existing Cursor assets in a target project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .versions import ASSET_DIRS


def detect_project(target: Path) -> dict[str, Any]:
    target = target.resolve()
    cursor = target / ".cursor"
    runtime = target / ".cursor-loop"
    detection: dict[str, Any] = {
        "target": str(target),
        "is_empty": not any(target.iterdir()) if target.exists() else True,
        "has_cursor": cursor.exists(),
        "has_runtime": runtime.exists(),
        "has_hooks_json": (cursor / "hooks.json").exists(),
        "has_commands": (cursor / "commands").exists(),
        "counts": {},
        "custom_files": [],
        "managed_files": [],
        "installed_version": None,
        "repository_kind": _classify_repo(target),
    }
    for name in ASSET_DIRS:
        directory = cursor / name
        files = [p for p in directory.rglob("*") if p.is_file()] if directory.exists() else []
        detection["counts"][name] = len(files)

    manifest = runtime / "install_manifest.json"
    managed_paths: set[str] = set()
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        detection["installed_version"] = data.get("framework_version") or data.get("version")
        for entry in data.get("files", []):
            if entry.get("path"):
                managed_paths.add(entry["path"])
                detection["managed_files"].append(entry["path"])

    if cursor.exists():
        for path in cursor.rglob("*"):
            if not path.is_file():
                continue
            rel = f".cursor/{path.relative_to(cursor).as_posix()}"
            if rel not in managed_paths and rel != ".cursor/hooks.json":
                # hooks.json may be managed; if not in manifest treat as custom only when content differs later
                if not managed_paths or rel not in managed_paths:
                    detection["custom_files"].append(rel)

    return detection


def _classify_repo(target: Path) -> str:
    if not target.exists() or not any(target.iterdir()):
        return "empty"
    markers = {
        "package.json": "node",
        "pyproject.toml": "python",
        "Cargo.toml": "rust",
        "pubspec.yaml": "flutter",
        "settings.gradle": "android",
        "settings.gradle.kts": "android",
        "go.mod": "go",
    }
    found = [kind for name, kind in markers.items() if (target / name).exists()]
    # monorepo heuristics
    packages = target / "packages"
    apps = target / "apps"
    if packages.exists() or apps.exists() or len(found) > 1:
        return "monorepo" if (packages.exists() or apps.exists() or len(found) > 1) else (found[0] if found else "generic")
    if found:
        return found[0]
    # size heuristic
    file_count = sum(1 for _ in target.rglob("*") if _.is_file())
    if file_count > 5000:
        return "large"
    if file_count < 20:
        return "small"
    return "generic"
