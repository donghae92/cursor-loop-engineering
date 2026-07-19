#!/usr/bin/env python3
"""Cursor Loop Engineering CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from cursor_loop.paths import ensure_sys_path, framework_root

ensure_sys_path()

from cursor_loop_runtime.checkpoint_manager import CheckpointManager  # noqa: E402
from cursor_loop_runtime.evidence_controller import EvidenceController  # noqa: E402
from cursor_loop_runtime.loop_controller import LoopController  # noqa: E402
from cursor_loop_runtime.memory_controller import MemoryController  # noqa: E402
from cursor_loop_runtime.models import read_json, utcnow, write_json_atomic  # noqa: E402
from cursor_loop_runtime.regression_controller import RegressionController  # noqa: E402
from cursor_loop_runtime.scheduler import Scheduler  # noqa: E402
from cursor_loop_runtime.state_machine import StateMachine  # noqa: E402


def _print(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_bootstrap(args: argparse.Namespace) -> int:
    """Bootstrap this repository's own .cursor-loop and self-install assets."""
    root = framework_root() if args.self else Path(args.path).resolve()
    memory = MemoryController(root)
    created = memory.ensure()
    StateMachine(root).mark_healthy("bootstrap")
    Scheduler(root).run()
    CheckpointManager(root).create("bootstrap")
    out = {
        "result": "PASS",
        "root": str(root),
        "runtime": created,
        "bootstrapped_at": utcnow(),
    }
    _print(out)
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    install_mod = framework_root() / "install" / "install.py"
    import importlib.util

    spec = importlib.util.spec_from_file_location("cle_install", install_mod)
    if spec is None or spec.loader is None:
        _print({"result": "FAIL", "error": "installer not found"})
        return 2
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.install_into(Path(args.target), force=args.force)
    _print(result)
    return 0 if result.get("result") == "PASS" else 4


def cmd_verify(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    memory = MemoryController(root)
    memory.ensure()
    failures: list[str] = []
    checks: dict[str, str] = {}

    required = [
        root / ".cursor" / "hooks.json",
        root / ".cursor" / "rules",
        root / ".cursor" / "skills",
        root / ".cursor" / "agents",
        root / ".cursor" / "hooks",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        failures.extend(f"missing: {item}" for item in missing)
    checks["infrastructure"] = "PASS" if not missing else "FAIL"

    # Required rules
    rule_names = [
        "architecture",
        "coding-standards",
        "validation-policy",
        "regression-policy",
        "evidence-policy",
        "loop-policy",
        "research-policy",
        "review-policy",
        "release-policy",
        "safety-policy",
        "performance-policy",
        "documentation-policy",
    ]
    for name in rule_names:
        path = root / ".cursor" / "rules" / f"{name}.mdc"
        if not path.exists():
            failures.append(f"missing rule: {name}.mdc")
    checks["rules"] = "PASS" if not any(f.startswith("missing rule:") for f in failures) else "FAIL"

    skill_names = [
        "runtime-repair",
        "graph-builder",
        "regression-check",
        "validation",
        "research",
        "release",
        "report",
        "scheduler",
        "loop",
        "memory",
        "hash-audit",
        "bootstrap",
        "repository-analysis",
        "architecture-review",
    ]
    for name in skill_names:
        path = root / ".cursor" / "skills" / name / "SKILL.md"
        if not path.exists():
            failures.append(f"missing skill: {name}")
    checks["skills"] = "PASS" if not any(f.startswith("missing skill:") for f in failures) else "FAIL"

    agent_names = [
        "ceo",
        "manager",
        "planner",
        "researcher",
        "developer",
        "reviewer",
        "qa",
        "regression",
        "release",
        "documentation",
    ]
    for name in agent_names:
        path = root / ".cursor" / "agents" / f"{name}.md"
        if not path.exists():
            failures.append(f"missing agent: {name}.md")
    checks["agents"] = "PASS" if not any(f.startswith("missing agent:") for f in failures) else "FAIL"

    hook_names = [
        "pre_task.py",
        "post_task.py",
        "loop_continue.py",
        "stop.py",
        "failure.py",
        "research.py",
        "validation.py",
    ]
    for name in hook_names:
        path = root / ".cursor" / "hooks" / name
        if not path.exists():
            failures.append(f"missing hook: {name}")
    checks["hooks"] = "PASS" if not any(f.startswith("missing hook:") for f in failures) else "FAIL"

    t0 = time.perf_counter()
    regress = RegressionController(root).run()
    memory.record_timing("validate", (time.perf_counter() - t0) * 1000.0, regress.get("result") == "PASS")
    checks["regress"] = regress.get("result", "FAIL")
    if regress.get("result") != "PASS":
        failures.append("regress failed")
        failures.extend(regress.get("failures") or [])

    evidence = EvidenceController(root).check()
    checks["evidence"] = evidence.get("result", "FAIL")
    if evidence.get("result") != "PASS":
        failures.append("evidence failed")

    schedule = Scheduler(root).run()
    checks["schedule"] = schedule.get("result", "FAIL")

    result = {
        "result": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "checks": checks,
        "verified_at": utcnow(),
        "root": str(root),
    }
    write_json_atomic(memory.paths.runtime_dir / "last_verify.json", result)
    if result["result"] == "PASS":
        StateMachine(root).mark_healthy("verify passed")
    else:
        StateMachine(root).mark_repairing("verify failed")
    memory.log_event("VERIFY", "NOTICE" if not failures else "ERROR", result["result"])
    _print(result)
    return 0 if not failures else 4


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    issues: list[str] = []
    py = sys.version_info
    if py < (3, 9):
        issues.append(f"Python 3.9+ required; found {py.major}.{py.minor}")
    if not (framework_root() / "runtime" / "cursor_loop_runtime").exists():
        issues.append("runtime package missing from framework root")
    if not (root / ".cursor").exists():
        issues.append(".cursor directory missing — run: cle install .")
    if not (root / ".cursor-loop").exists():
        issues.append(".cursor-loop missing — run: cle bootstrap")
    hooks = root / ".cursor" / "hooks.json"
    if hooks.exists():
        try:
            data = json.loads(hooks.read_text(encoding="utf-8"))
            if data.get("version") != 1:
                issues.append("hooks.json version must be 1")
        except json.JSONDecodeError:
            issues.append("hooks.json is not valid JSON")
    for script in (root / ".cursor" / "hooks").glob("*.py") if (root / ".cursor" / "hooks").exists() else []:
        if not script.stat().st_mode & 0o111:
            issues.append(f"hook not executable: {script.name}")
    out = {
        "result": "PASS" if not issues else "FAIL",
        "issues": issues,
        "python": f"{py.major}.{py.minor}.{py.micro}",
        "framework_root": str(framework_root()),
        "project_root": str(root),
        "checked_at": utcnow(),
    }
    _print(out)
    return 0 if not issues else 4


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
    out = {
        "state": memory.get_state(),
        "loop_state": memory.get_loop_state().to_dict(),
        "performance": read_json(memory.paths.performance, {}),
        "schedule": Scheduler(root).queue.summary(),
        "checkpoints": CheckpointManager(root).list_checkpoints(),
        "recent_events": memory.recent_events(10),
    }
    _print(out)
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Reinstall framework assets into the target project."""
    args.target = args.path
    args.force = True
    return cmd_install(args)


def cmd_repair(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    memory = MemoryController(root)
    StateMachine(root).mark_repairing("repair requested")
    memory.ensure()
    # Ensure hook scripts executable
    hooks = root / ".cursor" / "hooks"
    repaired: list[str] = []
    if hooks.exists():
        for script in hooks.glob("*.py"):
            mode = script.stat().st_mode
            if not mode & 0o111:
                script.chmod(mode | 0o111)
                repaired.append(script.name)
    # Recreate missing runtime files
    created = memory.ensure()
    Scheduler(root).run()
    verify_args = argparse.Namespace(path=str(root))
    rc = cmd_verify(verify_args)
    out = {
        "result": "PASS" if rc == 0 else "FAIL",
        "repaired_hooks": repaired,
        "runtime": created,
        "verify_exit_code": rc,
    }
    _print(out)
    return rc


def cmd_release(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    memory = MemoryController(root)
    verify_args = argparse.Namespace(path=str(root))
    rc = cmd_verify(verify_args)
    if rc != 0:
        _print({"result": "FAIL", "reason": "verify failed; release blocked"})
        return 4
    checkpoint = CheckpointManager(root).create("release")
    StateMachine(root).transition("READY_FOR_RELEASE", "release gates passed")
    memory.append_decision("RELEASE", "PASS", "Release checkpoint created", checkpoint=checkpoint["checkpoint_id"])
    out = {
        "result": "PASS",
        "checkpoint": checkpoint,
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
    p_install.add_argument("--force", action="store_true")
    p_install.set_defaults(func=cmd_install)

    p_verify = sub.add_parser("verify", help="Verify installation and run regressions")
    p_verify.add_argument("--path", default=".", help="Project path")
    p_verify.set_defaults(func=cmd_verify)

    p_doctor = sub.add_parser("doctor", help="Environment and installation diagnostics")
    p_doctor.add_argument("--path", default=".", help="Project path")
    p_doctor.set_defaults(func=cmd_doctor)

    p_loop = sub.add_parser("loop", help="Advance or inspect the engineering loop")
    p_loop.add_argument("--path", default=".", help="Project path")
    p_loop.add_argument("--once", action="store_true", default=True)
    p_loop.add_argument("--status", action="store_true")
    p_loop.set_defaults(func=cmd_loop)

    p_status = sub.add_parser("status", help="Show runtime status")
    p_status.add_argument("--path", default=".", help="Project path")
    p_status.set_defaults(func=cmd_status)

    p_update = sub.add_parser("update", help="Reinstall/update framework assets")
    p_update.add_argument("--path", default=".", help="Project path")
    p_update.set_defaults(func=cmd_update)

    p_repair = sub.add_parser("repair", help="Repair installation and re-verify")
    p_repair.add_argument("--path", default=".", help="Project path")
    p_repair.set_defaults(func=cmd_repair)

    p_release = sub.add_parser("release", help="Create release checkpoint after verify PASS")
    p_release.add_argument("--path", default=".", help="Project path")
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
