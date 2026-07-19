"""Migration engine — upgrade and rollback between framework versions."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

from cursor_loop_runtime.models import append_jsonl, read_json, utcnow, write_json_atomic

from .versions import compare_semver, framework_root, read_framework_version


def load_registry(root: Path | None = None) -> dict[str, Any]:
    root = root or framework_root()
    path = root / "migration" / "registry.json"
    if not path.exists():
        return {"migrations": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_script(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load migration script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def migration_history_path(target: Path) -> Path:
    return target / ".cursor-loop" / "migration_history.jsonl"


def installed_version(target: Path) -> str | None:
    manifest = target / ".cursor-loop" / "install_manifest.json"
    if not manifest.exists():
        return None
    data = read_json(manifest, {})
    return data.get("framework_version") or data.get("version")


def plan_upgrade(target: Path, to_version: str | None = None) -> list[dict[str, Any]]:
    current = installed_version(target) or "0.0.0"
    desired = to_version or read_framework_version()
    registry = load_registry()
    steps = []
    for item in registry.get("migrations", []):
        frm = item["from_version"]
        to = item["to_version"]
        if compare_semver(frm, current) >= 0 and compare_semver(to, current) > 0 and compare_semver(to, desired) <= 0:
            steps.append(item)
        elif compare_semver(current, frm) == 0 and compare_semver(to, desired) <= 0:
            steps.append(item)
    # Filter strictly: from matches walking path
    ordered = []
    cursor = current
    remaining = list(registry.get("migrations", []))
    safety = 0
    while compare_semver(cursor, desired) < 0 and safety < 50:
        safety += 1
        match = next((m for m in remaining if m["from_version"] == cursor), None)
        if match is None:
            # allow 0.0.0 / missing install to jump via first migration whose to <= desired
            if cursor in {"0.0.0", None} or not installed_version(target):
                match = next(
                    (
                        m
                        for m in remaining
                        if compare_semver(m["to_version"], desired) <= 0
                        and m["from_version"] == "1.0.0"
                        and desired == "1.1.0"
                    ),
                    None,
                )
                if match is None and compare_semver(desired, "1.1.0") == 0:
                    # fresh install path — no migration required
                    break
            if match is None:
                break
        ordered.append(match)
        cursor = match["to_version"]
    return ordered


def _record(target: Path, record: dict[str, Any]) -> None:
    append_jsonl(migration_history_path(target), record)


def run_upgrade(target: Path, to_version: str | None = None) -> dict[str, Any]:
    root = framework_root()
    starting = installed_version(target) or "0.0.0"
    steps = plan_upgrade(target, to_version)
    applied: list[str] = []
    for step in steps:
        script = root / step["upgrade"]
        module = _load_script(script)
        result = module.upgrade(target, framework_root=root)
        applied.append(step["id"])
        _record(
            target,
            {
                "action": "upgrade",
                "migration_id": step["id"],
                "from_version": step["from_version"],
                "to_version": step["to_version"],
                "result": result.get("result", "PASS"),
                "timestamp": utcnow(),
                "details": result,
            },
        )
        if result.get("result") != "PASS":
            return {"result": "FAIL", "applied": applied, "failed": step["id"], "details": result}

    # Update manifest version
    manifest_path = target / ".cursor-loop" / "install_manifest.json"
    manifest = read_json(manifest_path, {})
    manifest["framework_version"] = to_version or read_framework_version()
    manifest["version"] = manifest["framework_version"]
    manifest["installed_version"] = manifest["framework_version"]
    manifest["updated_at"] = utcnow()
    write_json_atomic(manifest_path, manifest)
    return {
        "result": "PASS",
        "from_version": starting,
        "to_version": manifest["framework_version"],
        "applied": applied,
        "steps_planned": [s["id"] for s in steps],
    }


def run_rollback(target: Path, migration_id: str | None = None) -> dict[str, Any]:
    root = framework_root()
    registry = load_registry()
    history_path = migration_history_path(target)
    if not history_path.exists():
        return {"result": "FAIL", "error": "no migration history"}
    lines = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    upgrades = [row for row in lines if row.get("action") == "upgrade" and row.get("result") == "PASS"]
    if not upgrades:
        return {"result": "FAIL", "error": "no successful upgrades to roll back"}
    target_row = None
    if migration_id:
        target_row = next((row for row in reversed(upgrades) if row.get("migration_id") == migration_id), None)
    else:
        target_row = upgrades[-1]
    if not target_row:
        return {"result": "FAIL", "error": f"migration not found: {migration_id}"}
    step = next((m for m in registry.get("migrations", []) if m["id"] == target_row["migration_id"]), None)
    if not step:
        return {"result": "FAIL", "error": "migration registry entry missing"}
    script = root / step["rollback"]
    module = _load_script(script)
    result = module.rollback(target, framework_root=root)
    _record(
        target,
        {
            "action": "rollback",
            "migration_id": step["id"],
            "from_version": step["to_version"],
            "to_version": step["from_version"],
            "result": result.get("result", "PASS"),
            "timestamp": utcnow(),
            "details": result,
        },
    )
    manifest_path = target / ".cursor-loop" / "install_manifest.json"
    manifest = read_json(manifest_path, {})
    manifest["framework_version"] = step["from_version"]
    manifest["version"] = step["from_version"]
    manifest["updated_at"] = utcnow()
    write_json_atomic(manifest_path, manifest)
    return {
        "result": result.get("result", "PASS"),
        "rolled_back": step["id"],
        "installed_version": step["from_version"],
        "details": result,
    }
