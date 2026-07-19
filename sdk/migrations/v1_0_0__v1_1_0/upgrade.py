#!/usr/bin/env python3
"""Upgrade 1.0.0 -> 1.1.0"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def upgrade(target: Path, framework_root: Path | None = None) -> dict[str, Any]:
    runtime = target / ".cursor-loop"
    runtime.mkdir(parents=True, exist_ok=True)
    history = runtime / "migration_history.jsonl"
    if not history.exists():
        history.write_text("", encoding="utf-8")
    backups = runtime / "backups"
    backups.mkdir(parents=True, exist_ok=True)

    manifest_path = runtime / "install_manifest.json"
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = {
            "framework": "cursor-loop-engineering",
            "files": [],
        }
    data["framework_version"] = "1.1.0"
    data["version"] = "1.1.0"
    data["installed_version"] = "1.1.0"
    data["repository_version"] = "1.1.0"
    data.setdefault("migration_notes", []).append("upgraded to install framework 1.1.0")
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    versions = runtime / "versions.json"
    versions.write_text(
        json.dumps(
            {
                "framework_version": "1.1.0",
                "repository_version": "1.1.0",
                "installed_version": "1.1.0",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"result": "PASS", "migrated_to": "1.1.0", "created": ["migration_history.jsonl", "backups/", "versions.json"]}
