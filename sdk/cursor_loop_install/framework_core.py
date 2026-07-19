"""Core framework installer API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cursor_loop_runtime.checkpoint_manager import CheckpointManager
from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import utcnow, write_json_atomic
from cursor_loop_runtime.scheduler import Scheduler
from cursor_loop_runtime.state_machine import StateMachine

from .backup import restore_backup
from .detector import detect_project
from .doctor import doctor as run_doctor
from .merger import install_assets
from .migration_engine import run_rollback, run_upgrade
from .verify import verify_framework
from .versions import framework_root, read_compatibility, read_framework_version


def bootstrap(target: Path) -> dict[str, Any]:
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    memory = MemoryController(target)
    created = memory.ensure()
    StateMachine(target).mark_healthy("bootstrap")
    Scheduler(target).run()
    checkpoint = CheckpointManager(target).create("bootstrap")
    return {
        "result": "PASS",
        "root": str(target),
        "runtime": created,
        "checkpoint": checkpoint,
        "bootstrapped_at": utcnow(),
        "detection": detect_project(target),
    }


def install_into(
    target: Path,
    *,
    force: bool = False,
    source_root: Path | None = None,
    preserve_custom: bool = True,
) -> dict[str, Any]:
    target = target.resolve()
    if not target.exists() or not target.is_dir():
        raise FileNotFoundError(f"target project not found: {target}")

    source_root = (source_root or framework_root()).resolve()
    detection = detect_project(target)
    memory = MemoryController(target)
    memory.ensure()

    merge = install_assets(
        target,
        force=force,
        preserve_custom=preserve_custom,
        source_root=source_root,
    )

    version = read_framework_version(source_root)
    # Prefer package.json version when importing a release archive
    package_json = source_root / "package.json"
    if package_json.exists():
        try:
            version = json.loads(package_json.read_text(encoding="utf-8")).get("version") or version
        except json.JSONDecodeError:
            pass

    agents_md = target / "AGENTS.md"
    if not agents_md.exists():
        agents_md.write_text(
            "# AGENTS.md\n\n"
            "This project uses **Cursor Loop Engineering**.\n\n"
            "## Quick commands\n\n"
            "```bash\n"
            "python3 -m cursor_loop status\n"
            "python3 -m cursor_loop verify\n"
            "python3 -m cursor_loop update\n"
            "python3 -m cursor_loop doctor --repair\n"
            "```\n\n"
            "Runtime memory lives in `.cursor-loop/`.\n"
            "Cursor assets live in `.cursor/`.\n",
            encoding="utf-8",
        )

    compat = read_compatibility(source_root)
    previous = detection.get("installed_version")

    # Preserve previous version in manifest until migrations finish
    interim = {
        "framework": "cursor-loop-engineering",
        "framework_version": previous or version,
        "version": previous or version,
        "repository_version": version,
        "installed_version": previous or version,
        "installed_at": utcnow(),
        "updated_at": utcnow(),
        "source": str(source_root),
        "target": str(target),
        "repository_kind": detection.get("repository_kind"),
        "compatibility": compat.get("current_version"),
        "files": merge.get("files") or [],
        "self_install": bool(merge.get("self_install")),
        "backup": merge.get("backup"),
    }
    write_json_atomic(memory.paths.manifest, interim)

    upgrade = None
    if previous and previous != version:
        upgrade = run_upgrade(target, version)
    elif not previous:
        # Fresh install — record target version directly
        pass

    manifest = {
        **interim,
        "framework_version": version,
        "version": version,
        "installed_version": version,
        "repository_version": version,
        "updated_at": utcnow(),
    }
    write_json_atomic(memory.paths.manifest, manifest)
    StateMachine(target).mark_healthy("framework installed")
    Scheduler(target).run()
    memory.log_event("INSTALL", "NOTICE", f"Installed {version} into {target}", file_count=len(manifest["files"]))

    return {
        "result": "PASS",
        "target": str(target),
        "framework_version": version,
        "file_count": len(manifest["files"]),
        "detection": detection,
        "merge": {
            "written": len(merge.get("written") or []),
            "updated": len(merge.get("updated") or []),
            "backed_up": merge.get("backed_up") or [],
            "self_install": merge.get("self_install"),
        },
        "upgrade": upgrade,
        "manifest": str(memory.paths.manifest),
        "runtime": {
            "runtime_dir": str(memory.paths.runtime_dir),
            "state": str(memory.paths.state),
            "loop_state": str(memory.paths.loop_state),
        },
    }


def update(target: Path, *, force: bool = False) -> dict[str, Any]:
    target = target.resolve()
    before = detect_project(target)
    # If an older version is installed, migrate before rewriting manifest to latest
    migrated = {"result": "PASS", "applied": [], "steps_planned": []}
    if before.get("installed_version") and before["installed_version"] != read_framework_version():
        migrated = run_upgrade(target, read_framework_version())
    installed = install_into(target, force=force, preserve_custom=True)
    verification = verify_framework(target)
    return {
        "result": "PASS"
        if installed.get("result") == "PASS"
        and verification.get("result") == "PASS"
        and migrated.get("result") == "PASS"
        else "FAIL",
        "before_version": before.get("installed_version"),
        "after_version": installed.get("framework_version"),
        "install": installed,
        "migration": migrated,
        "verify": verification,
        "updated_at": utcnow(),
    }


def repair(target: Path) -> dict[str, Any]:
    target = target.resolve()
    diagnosis = run_doctor(target, repair=True)
    verification = verify_framework(target)
    return {
        "result": "PASS" if diagnosis.get("result") in {"PASS", "REPAIRED"} and verification.get("result") == "PASS" else "FAIL",
        "doctor": diagnosis,
        "verify": verification,
        "repaired_at": utcnow(),
    }


def remove_framework(target: Path, *, keep_custom: bool = True, purge_runtime: bool = False) -> dict[str, Any]:
    import shutil

    target = target.resolve()
    memory = MemoryController(target)
    memory.ensure()
    manifest = memory.paths.manifest
    removed: list[str] = []
    retained: list[str] = []
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for entry in data.get("files", []):
            rel = entry.get("path")
            if not rel:
                continue
            path = target / rel
            if not path.exists():
                continue
            if keep_custom and rel == ".cursor/hooks.json":
                retained.append(rel)
                continue
            path.unlink()
            removed.append(rel)
            parent = path.parent
            while parent != target / ".cursor" and parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent

    memory.log_event("REMOVE", "NOTICE", "Framework assets removed", removed=len(removed))

    if purge_runtime and memory.paths.runtime_dir.exists():
        shutil.rmtree(memory.paths.runtime_dir)
        removed.append(".cursor-loop")
    elif memory.paths.runtime_dir.exists():
        state = memory.get_state()
        state["phase"] = "UNINITIALIZED"
        state["health"] = "REMOVED"
        write_json_atomic(memory.paths.state, state)
        if manifest.exists():
            manifest.unlink()
            removed.append(".cursor-loop/install_manifest.json")

    return {
        "result": "PASS",
        "removed": removed,
        "retained": retained,
        "purge_runtime": purge_runtime,
        "removed_at": utcnow(),
    }


def rollback(target: Path, migration_id: str | None = None) -> dict[str, Any]:
    result = run_rollback(target, migration_id=migration_id)
    if result.get("result") == "PASS":
        # also attempt latest backup restore if present in details
        details = result.get("details") or {}
        backup_id = details.get("backup_id")
        if backup_id:
            restore_backup(target, backup_id)
    return result
