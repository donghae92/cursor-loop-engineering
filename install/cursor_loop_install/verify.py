"""Framework verification across rules, skills, hooks, agents, and runtime."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from cursor_loop_runtime.evidence_controller import EvidenceController
from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import utcnow, write_json_atomic
from cursor_loop_runtime.regression_controller import RegressionController
from cursor_loop_runtime.scheduler import Scheduler
from cursor_loop_runtime.state_machine import StateMachine

REQUIRED_RULES = [
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

REQUIRED_SKILLS = [
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

REQUIRED_AGENTS = [
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

REQUIRED_HOOKS = [
    "pre_task.py",
    "post_task.py",
    "loop_continue.py",
    "stop.py",
    "failure.py",
    "research.py",
    "validation.py",
]


def verify_framework(root: Path) -> dict[str, Any]:
    root = root.resolve()
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
        root / ".cursor-loop",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        failures.extend(f"missing: {item}" for item in missing)
    checks["infrastructure"] = "PASS" if not missing else "FAIL"

    for name in REQUIRED_RULES:
        if not (root / ".cursor" / "rules" / f"{name}.mdc").exists():
            failures.append(f"missing rule: {name}.mdc")
    checks["rules"] = "PASS" if not any(f.startswith("missing rule:") for f in failures) else "FAIL"

    for name in REQUIRED_SKILLS:
        if not (root / ".cursor" / "skills" / name / "SKILL.md").exists():
            failures.append(f"missing skill: {name}")
    checks["skills"] = "PASS" if not any(f.startswith("missing skill:") for f in failures) else "FAIL"

    for name in REQUIRED_AGENTS:
        if not (root / ".cursor" / "agents" / f"{name}.md").exists():
            failures.append(f"missing agent: {name}.md")
    checks["agents"] = "PASS" if not any(f.startswith("missing agent:") for f in failures) else "FAIL"

    for name in REQUIRED_HOOKS:
        if not (root / ".cursor" / "hooks" / name).exists():
            failures.append(f"missing hook: {name}")
    checks["hooks"] = "PASS" if not any(f.startswith("missing hook:") for f in failures) else "FAIL"

    hooks_json = root / ".cursor" / "hooks.json"
    if hooks_json.exists():
        try:
            data = json.loads(hooks_json.read_text(encoding="utf-8"))
            if data.get("version") != 1:
                failures.append("hooks.json version must be 1")
                checks["hooks_json"] = "FAIL"
            else:
                checks["hooks_json"] = "PASS"
        except json.JSONDecodeError as exc:
            failures.append(f"hooks.json invalid: {exc}")
            checks["hooks_json"] = "FAIL"
    else:
        checks["hooks_json"] = "FAIL"

    # Runtime / scheduler / regression / evidence / memory
    for key in ("state.json", "loop_state.json", "performance.json", "task_queue.jsonl"):
        if not (root / ".cursor-loop" / key).exists():
            failures.append(f"missing runtime: .cursor-loop/{key}")
    checks["runtime"] = "PASS" if not any(f.startswith("missing runtime:") for f in failures) else "FAIL"

    t0 = time.perf_counter()
    schedule = Scheduler(root).run()
    checks["scheduler"] = schedule.get("result", "FAIL")
    if schedule.get("result") != "PASS":
        failures.append("scheduler failed")

    regress = RegressionController(root).run()
    memory.record_timing("validate", (time.perf_counter() - t0) * 1000.0, regress.get("result") == "PASS")
    checks["regression"] = regress.get("result", "FAIL")
    if regress.get("result") != "PASS":
        failures.append("regression failed")
        failures.extend(regress.get("failures") or [])

    evidence = EvidenceController(root).check()
    checks["evidence"] = evidence.get("result", "FAIL")
    if evidence.get("result") != "PASS":
        failures.append("evidence failed")

    checks["memory"] = "PASS" if (root / ".cursor-loop" / "events.jsonl").exists() else "FAIL"
    if checks["memory"] != "PASS":
        failures.append("memory events log missing")

    # optional commands dir is user-owned; just report
    checks["commands"] = "PRESENT" if (root / ".cursor" / "commands").exists() else "ABSENT"

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
    return result
