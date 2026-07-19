#!/usr/bin/env python3
"""Rollback 1.1.0 -> 1.0.0"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def rollback(target: Path, framework_root: Path | None = None) -> dict[str, Any]:
    runtime = target / ".cursor-loop"
    manifest_path = runtime / "install_manifest.json"
    if not manifest_path.exists():
        return {"result": "FAIL", "error": "install_manifest.json missing"}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["framework_version"] = "1.0.0"
    data["version"] = "1.0.0"
    data["installed_version"] = "1.0.0"
    data["repository_version"] = "1.0.0"
    notes = data.get("migration_notes") or []
    notes.append("rolled back to 1.0.0")
    data["migration_notes"] = notes
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    versions = runtime / "versions.json"
    versions.write_text(
        json.dumps(
            {
                "framework_version": "1.0.0",
                "repository_version": "1.0.0",
                "installed_version": "1.0.0",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"result": "PASS", "rolled_back_to": "1.0.0"}
