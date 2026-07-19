#!/usr/bin/env python3
"""Upgrade 1.1.0 -> 1.2.0 — Cursor Plugin packaging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def upgrade(target: Path, framework_root: Path | None = None) -> dict[str, Any]:
    runtime = target / ".cursor-loop"
    runtime.mkdir(parents=True, exist_ok=True)
    versions = {
        "framework_version": "1.2.0",
        "repository_version": "1.2.0",
        "installed_version": "1.2.0",
        "plugin": True,
    }
    (runtime / "versions.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")

    # Ensure project commands directory exists for slash commands when installed into a project
    commands = target / ".cursor" / "commands"
    commands.mkdir(parents=True, exist_ok=True)
    if framework_root:
        src = Path(framework_root) / "commands"
        copied = []
        if src.exists():
            for path in src.glob("*.md"):
                dest = commands / path.name
                if not dest.exists():
                    dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
                    copied.append(path.name)
        marker = runtime / "plugin_upgrade_1_2_0.json"
        marker.write_text(json.dumps({"copied_commands": copied}, indent=2) + "\n", encoding="utf-8")

    manifest_path = runtime / "install_manifest.json"
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["framework_version"] = "1.2.0"
        data["version"] = "1.2.0"
        data["installed_version"] = "1.2.0"
        data["plugin"] = True
        notes = data.get("migration_notes") or []
        notes.append("upgraded to Cursor Plugin packaging 1.2.0")
        data["migration_notes"] = notes
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    return {"result": "PASS", "migrated_to": "1.2.0", "plugin": True}
