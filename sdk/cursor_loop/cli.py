#!/usr/bin/env python3
"""Cursor Loop Engineering CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cursor_loop.paths import ensure_sys_path, framework_root

ensure_sys_path()

from cursor_loop_install.detector import detect_project  # noqa: E402
from cursor_loop_install.doctor import doctor as run_doctor  # noqa: E402
from cursor_loop_install.export_import import export_package, import_package  # noqa: E402
from cursor_loop_install.framework_core import (  # noqa: E402
    bootstrap,
    install_into,
    remove_framework,
    repair,
    rollback,
    update,
)
from cursor_loop_install.migration_engine import plan_upgrade  # noqa: E402
from cursor_loop_install.verify import verify_framework  # noqa: E402
from cursor_loop_install.versions import read_compatibility, read_framework_version  # noqa: E402
from cursor_loop_runtime.checkpoint_manager import CheckpointManager  # noqa: E402
from cursor_loop_runtime.loop_controller import LoopController  # noqa: E402
from cursor_loop_runtime.memory_controller import MemoryController  # noqa: E402
from cursor_loop_runtime.models import read_json, utcnow  # noqa: E402
from cursor_loop_runtime.scheduler import Scheduler  # noqa: E402
from cursor_loop_runtime.state_machine import StateMachine  # noqa: E402


def _print(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_bootstrap(args: argparse.Namespace) -> int:
    root = framework_root() if args.self else Path(args.path).resolve()
    _print(bootstrap(root))
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    result = install_into(Path(args.target), force=args.force, preserve_custom=not args.force)
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_verify(args: argparse.Namespace) -> int:
    result = verify_framework(Path(args.path).resolve())
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_doctor(args: argparse.Namespace) -> int:
    result = run_doctor(Path(args.path).resolve(), repair=args.repair)
    # Also ensure framework source tree is intact when diagnosing from a consumer project
    if not (framework_root() / "runtime" / "cursor_loop_runtime").exists():
        result.setdefault("issues", []).append("runtime package missing from framework root")
        if result.get("result") == "PASS":
            result["result"] = "FAIL"
    _print(result)
    return 0 if result.get("result") in {"PASS", "REPAIRED"} else 4


def cmd_loop(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    controller = LoopController(root)
    if args.status:
        _print(controller.status())
        return 0
    out = controller.run_once()
    _print(out)
    disposition = out.get("loop_state", {}).get("disposition")
    if disposition in {"SAFE_STOP", "MANUAL_REVIEW"}:
        return 3
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    memory = MemoryController(root)
    memory.ensure()
    manifest = read_json(memory.paths.manifest, {})
    out = {
        "framework_version": read_framework_version(),
        "installed_version": manifest.get("installed_version") or manifest.get("framework_version"),
        "repository_version": manifest.get("repository_version"),
        "compatibility": read_compatibility().get("current_version"),
        "detection": detect_project(root),
        "state": memory.get_state(),
        "loop_state": memory.get_loop_state().to_dict(),
        "performance": read_json(memory.paths.performance, {}),
        "schedule": Scheduler(root).queue.summary(),
        "upgrade_plan": [step["id"] for step in plan_upgrade(root)],
        "checkpoints": CheckpointManager(root).list_checkpoints(),
        "recent_events": memory.recent_events(10),
    }
    _print(out)
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    result = update(Path(args.path).resolve(), force=args.force)
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_repair(args: argparse.Namespace) -> int:
    result = repair(Path(args.path).resolve())
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_remove(args: argparse.Namespace) -> int:
    result = remove_framework(
        Path(args.path).resolve(),
        keep_custom=not args.purge_custom,
        purge_runtime=args.purge_runtime,
    )
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_export(args: argparse.Namespace) -> int:
    output = Path(args.output).resolve() if args.output else None
    result = export_package(output)
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_import(args: argparse.Namespace) -> int:
    result = import_package(Path(args.archive), Path(args.target), force=args.force)
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_rollback(args: argparse.Namespace) -> int:
    result = rollback(Path(args.path).resolve(), migration_id=args.migration_id)
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_release(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    memory = MemoryController(root)
    verification = verify_framework(root)
    if verification.get("result") != "PASS":
        _print({"result": "FAIL", "reason": "verify failed; release blocked", "verify": verification})
        return 4
    packaged = export_package(Path(args.output).resolve() if args.output else None)
    checkpoint = CheckpointManager(root).create("release")
    StateMachine(root).transition("READY_FOR_RELEASE", "release gates passed")
    memory.append_decision("RELEASE", "PASS", "Release checkpoint created", checkpoint=checkpoint["checkpoint_id"])
    out = {
        "result": "PASS",
        "checkpoint": checkpoint,
        "package": packaged,
        "released_at": utcnow(),
    }
    _print(out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cle", description="Cursor Loop Engineering CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_boot = sub.add_parser("bootstrap", help="Initialize runtime memory")
    p_boot.add_argument("--path", default=".", help="Project path")
    p_boot.add_argument("--self", action="store_true", help="Bootstrap the framework repository itself")
    p_boot.set_defaults(func=cmd_bootstrap)

    p_install = sub.add_parser("install", help="Install framework into a project")
    p_install.add_argument("target", nargs="?", default=".", help="Target project directory")
    p_install.add_argument("--force", action="store_true", help="Force refresh managed assets (backs up first)")
    p_install.set_defaults(func=cmd_install)

    p_verify = sub.add_parser("verify", help="Verify installation and run regressions")
    p_verify.add_argument("--path", default=".", help="Project path")
    p_verify.set_defaults(func=cmd_verify)

    p_doctor = sub.add_parser("doctor", help="Diagnose and optionally repair installation")
    p_doctor.add_argument("--path", default=".", help="Project path")
    p_doctor.add_argument("--repair", action="store_true", help="Attempt automatic repairs")
    p_doctor.set_defaults(func=cmd_doctor)

    p_loop = sub.add_parser("loop", help="Advance or inspect the engineering loop")
    p_loop.add_argument("--path", default=".", help="Project path")
    p_loop.add_argument("--once", action="store_true", default=True)
    p_loop.add_argument("--status", action="store_true")
    p_loop.set_defaults(func=cmd_loop)

    p_status = sub.add_parser("status", help="Show runtime and version status")
    p_status.add_argument("--path", default=".", help="Project path")
    p_status.set_defaults(func=cmd_status)

    p_update = sub.add_parser("update", help="Incremental update preserving customizations")
    p_update.add_argument("--path", default=".", help="Project path")
    p_update.add_argument("--force", action="store_true", help="Force managed asset refresh")
    p_update.set_defaults(func=cmd_update)

    p_repair = sub.add_parser("repair", help="Repair installation and re-verify")
    p_repair.add_argument("--path", default=".", help="Project path")
    p_repair.set_defaults(func=cmd_repair)

    p_remove = sub.add_parser("remove", help="Remove managed framework assets")
    p_remove.add_argument("--path", default=".", help="Project path")
    p_remove.add_argument("--purge-runtime", action="store_true", help="Also delete .cursor-loop")
    p_remove.add_argument("--purge-custom", action="store_true", help="Also overwrite/remove merged hooks.json")
    p_remove.set_defaults(func=cmd_remove)

    p_export = sub.add_parser("export", help="Package framework for GitHub Releases")
    p_export.add_argument("--output", help="Output directory (default: dist/)")
    p_export.set_defaults(func=cmd_export)

    p_import = sub.add_parser("import", help="Install from a release archive")
    p_import.add_argument("archive", help="Path to .tar.gz package")
    p_import.add_argument("--target", default=".", help="Target project directory")
    p_import.add_argument("--force", action="store_true")
    p_import.set_defaults(func=cmd_import)

    p_rollback = sub.add_parser("rollback", help="Roll back the last migration")
    p_rollback.add_argument("--path", default=".", help="Project path")
    p_rollback.add_argument("--migration-id", help="Specific migration id to roll back")
    p_rollback.set_defaults(func=cmd_rollback)

    p_release = sub.add_parser("release", help="Verify, checkpoint, and export release assets")
    p_release.add_argument("--path", default=".", help="Project path")
    p_release.add_argument("--output", help="Package output directory")
    p_release.set_defaults(func=cmd_release)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        _print({"result": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
