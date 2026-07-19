#!/usr/bin/env python3
"""Generate production Cursor assets for cursor-loop-engineering."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURSOR = ROOT / ".cursor"


RULES = {
    "architecture": """---
description: Layered architecture for Cursor Loop Engineering
alwaysApply: true
---

# Architecture

Framework layers: Rules → Skills → Agents → Hooks → Runtime Controllers → CLI.

## Boundaries

- Write derived runtime state under `.cursor-loop/` only.
- Installable Cursor assets live under `.cursor/`.
- Controllers live in `runtime/cursor_loop_runtime/`.
- CLI lives in `sdk/cursor_loop/`.

Prefer controllers and `cle` commands over ad-hoc scripts.
""",
    "coding-standards": """---
description: Coding standards for Cursor Loop Engineering Python modules
globs: "**/{runtime,sdk,install,scripts,tests}/**/*.py"
alwaysApply: false
---

# Coding Standards

- Target Python 3.10+.
- Use atomic JSON writes (temp file + replace).
- Fail with explicit error codes and JSON results from CLI commands.
- Never fabricate evidence, hashes, or test results.
- Keep modules interoperable through `cursor_loop_runtime.models`.
""",
    "validation-policy": """---
description: Validation policy — independent checks and gate failures
alwaysApply: true
---

# Validation Policy

- Workers implement; validators verify independently.
- Run `python3 -m cursor_loop verify` after infrastructure changes.
- Gate FAIL starts a repair loop via `cle repair` / `cle loop`.
- Unknown or skipped mandatory gates block release.
""",
    "regression-policy": """---
description: Regression policy with L1–L8 levels and fixed baselines
alwaysApply: true
---

# Regression Policy

Every critical change triggers regression.

## Levels

L1 Schema · L2 Hash · L3 Provenance · L4 Semantic · L5 Temporal · L6 Dependency · L7 Representative · L8 Boot

Baselines must include artifact id, version, and hash. No floating baselines.
""",
    "evidence-policy": """---
description: Evidence policy — confidence is not evidence
alwaysApply: true
---

# Evidence Policy

Model confidence is never evidence.

Cite file paths, hashes, schemas, command outputs, or runtime artifacts.
Quarantine ambiguous outputs under `.cursor-loop/quarantine/`.
Use evidence checks before promoting claims.
""",
    "loop-policy": """---
description: Failed-section loop limits and stop dispositions
alwaysApply: true
---

# Loop Policy

Failed gate → localize → repair → re-validate → re-regress → recompute disposition.

Continue only while a concrete failure, corrective action, new evidence, retry budget, and measurable progress exist.

Otherwise stop with SAFE_STOP or MANUAL_REVIEW.
""",
    "research-policy": """---
description: Research policy for read-only investigation before changes
alwaysApply: true
---

# Research Policy

- Prefer read-only exploration before edits.
- Cite sources with paths and identifiers.
- Separate observation, interpretation, and recommendation.
- Do not mutate production artifacts during research.
""",
    "review-policy": """---
description: Independent review policy for derived changes
alwaysApply: true
---

# Review Policy

Reviewers do not author replacement implementations inside a review decision.

Report Critical / Suggestion / Nice-to-have with evidence.
Confirm validation and regression artifacts exist for the change.
""",
    "release-policy": """---
description: Release policy — verify must pass before packaging
alwaysApply: true
---

# Release Policy

Release requires `cle verify` PASS, healthy runtime state, and a release checkpoint.

Do not release with failed, unknown, or skipped mandatory gates.
Compiler/release agents must not invent new reasoning content.
""",
    "safety-policy": """---
description: Safety policy for destructive actions and secrets
alwaysApply: true
---

# Safety Policy

- Never commit secrets, tokens, or credentials.
- Ask before destructive irreversible operations outside `.cursor-loop/`.
- Hooks may deny unsafe shell mutations.
- Prefer fail-closed for destructive actions.
""",
    "performance-policy": """---
description: Performance policy for loops, hooks, and verification
alwaysApply: true
---

# Performance Policy

- Keep hooks fast; avoid heavy work on every keystroke.
- Record timings in `.cursor-loop/performance.json`.
- Cap expensive scans; prefer incremental checks.
- Optimize for short agent sessions with durable memory.
""",
    "documentation-policy": """---
description: Documentation policy for framework changes
alwaysApply: true
---

# Documentation Policy

- Update docs when CLI, hooks, or runtime contracts change.
- Keep Quick Start accurate and runnable.
- Prefer examples that execute, not aspirational snippets.
- Changelog every user-visible change.
""",
}


SKILLS = {
    "runtime-repair": ("Diagnoses degraded Cursor Loop runtime and repairs install/runtime artifacts.", """# Runtime Repair

1. `python3 -m cursor_loop status`
2. `python3 -m cursor_loop doctor`
3. `python3 -m cursor_loop repair`
4. Re-run `python3 -m cursor_loop verify`

Stop on SAFE_STOP / MANUAL_REVIEW or when source mutation outside the project is required.
"""),
    "graph-builder": ("Builds or documents dependency/architecture graphs for a project using framework conventions.", """# Graph Builder

1. Inventory modules under `runtime/`, `sdk/`, and project source.
2. Emit a structured graph JSON under `.cursor-loop/` or docs.
3. Cite real paths only; do not invent nodes.
"""),
    "regression-check": ("Runs regression controller and interprets L1–L8 results.", """# Regression Check

```bash
python3 -m cursor_loop verify
```

Inspect `.cursor-loop/regression_history.jsonl`. On FAIL, repair then re-run.
"""),
    "validation": ("Runs framework verification and interprets gate failures.", """# Validation

```bash
python3 -m cursor_loop verify
python3 -m cursor_loop doctor
```

Workers must not self-approve. Cite `last_verify.json`.
"""),
    "research": ("Read-only research across docs, runtime state, and repository structure.", """# Research

Read `docs/`, `.cursor/`, and `.cursor-loop/`. Return citations. No mutations.
"""),
    "release": ("Creates a release checkpoint after verify PASS.", """# Release

```bash
python3 -m cursor_loop verify
python3 -m cursor_loop release
```

Blocked if any mandatory gate failed.
"""),
    "report": ("Writes structured reports from runtime status and verification artifacts.", """# Report

Gather `status`, `last_verify.json`, regression history, and decisions.
Write JSON under `docs/` or project reports directory with evidence paths.
"""),
    "scheduler": ("Synchronizes the task queue and promotes backlog items.", """# Scheduler

Use the scheduler via status/repair flows or Python:

```python
from cursor_loop_runtime.scheduler import Scheduler
Scheduler().run()
```
"""),
    "loop": ("Advances the failed-section engineering loop.", """# Loop

```bash
python3 -m cursor_loop loop --once
python3 -m cursor_loop loop --status
```

Use Cursor `/loop` for recurring ticks while disposition is CONTINUE.
"""),
    "memory": ("Inspects and maintains durable `.cursor-loop` runtime memory.", """# Memory

Memory files: `state.json`, `loop_state.json`, `task_queue.jsonl`, histories, `performance.json`.
Use MemoryController.ensure() and never hand-edit partially.
"""),
    "hash-audit": ("Audits install manifest hashes against on-disk Cursor assets.", """# Hash Audit

Regression L2 compares `.cursor-loop/install_manifest.json` hashes.
On mismatch, run `python3 -m cursor_loop update` then verify.
"""),
    "bootstrap": ("Bootstraps runtime memory and default tasks into a project.", """# Bootstrap

```bash
python3 -m cursor_loop bootstrap
python3 -m cursor_loop install .
python3 -m cursor_loop verify
```
"""),
    "repository-analysis": ("Analyzes repository structure for framework fit and gaps.", """# Repository Analysis

Inventory languages, build files, tests, and CI.
Map gaps to skills/rules/agents. Output a concrete adoption plan.
"""),
    "architecture-review": ("Reviews architecture against framework layering and boundaries.", """# Architecture Review

Check Rules→Skills→Agents→Hooks→Runtime layering.
Flag boundary violations and missing verification gates.
""",),
}


AGENTS = {
    "ceo": (True, "Supervisor for mission gates and stop dispositions.", "Decide CONTINUE / SAFE_STOP / MANUAL_REVIEW. Delegate; do not implement features."),
    "manager": (False, "Orchestrates queue advancement and verification cycles.", "Run schedule/verify/loop. Coordinate developer and qa agents."),
    "planner": (True, "Designs task DAGs; never executes.", "Produce ordered tasks, owners, acceptance criteria, and risks."),
    "researcher": (True, "Read-only repository and docs research.", "Cite paths. No mutations."),
    "developer": (False, "Implements framework and project-derived changes.", "Keep changes minimal; verify after edits."),
    "reviewer": (True, "Independent review of changes.", "Do not rewrite implementations inside the review decision."),
    "qa": (True, "Runs verify/doctor and interprets failures.", "Return concrete failures and repair owner."),
    "regression": (True, "Owns regression baselines and history interpretation.", "Reject floating baselines."),
    "release": (False, "Packages release checkpoints after gates pass.", "Never bypass failed verify."),
    "documentation": (False, "Updates docs and examples to match reality.", "Prefer runnable commands and accurate paths."),
}


HOOKS = {
    "pre_task.py": '''#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    raw = sys.stdin.read() or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    tool = payload.get("tool_name") or payload.get("tool") or ""
    print(json.dumps({
        "permission": "allow",
        "agent_message": f"Cursor Loop pre-task ({tool}): prefer cle verify/status; write runtime under .cursor-loop/ only."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
    "post_task.py": '''#!/usr/bin/env python3
import json, sys

def main() -> int:
    _ = sys.stdin.read()
    print(json.dumps({
        "additional_context": "Cursor Loop post-task: after derived changes run `python3 -m cursor_loop verify`."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
    "loop_continue.py": '''#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    _ = sys.stdin.read()
    root = Path.cwd()
    loop_path = root / ".cursor-loop" / "loop_state.json"
    out = {}
    if loop_path.exists():
        state = json.loads(loop_path.read_text(encoding="utf-8"))
        if state.get("disposition") == "CONTINUE":
            out["followup_message"] = (
                "Cursor Loop CONTINUE: run `python3 -m cursor_loop repair` then "
                "`python3 -m cursor_loop loop --once`."
            )
    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
    "stop.py": '''#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    _ = sys.stdin.read()
    loop_path = Path.cwd() / ".cursor-loop" / "loop_state.json"
    out = {}
    if loop_path.exists():
        state = json.loads(loop_path.read_text(encoding="utf-8"))
        disp = state.get("disposition")
        if disp == "CONTINUE" and state.get("last_result") == "FAIL":
            out["followup_message"] = "Cursor Loop: failed gate remains. Run cle repair && cle verify."
        elif disp in {"SAFE_STOP", "MANUAL_REVIEW"}:
            out["followup_message"] = f"Cursor Loop {disp}: stop identical failure loops and await review if needed."
    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
    "failure.py": '''#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    raw = sys.stdin.read() or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    events = Path.cwd() / ".cursor-loop" / "events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    with events.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "event_type": "TOOL_FAILURE",
            "payload_keys": sorted(list(payload.keys())),
        }) + "\\n")
    print(json.dumps({
        "additional_context": "Cursor Loop failure hook recorded an event. Consider `python3 -m cursor_loop doctor`."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
    "research.py": '''#!/usr/bin/env python3
import json, sys

def main() -> int:
    _ = sys.stdin.read()
    print(json.dumps({
        "additional_context": "Cursor Loop research: cite paths; do not mutate; separate observation from interpretation."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
    "validation.py": '''#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    _ = sys.stdin.read()
    verify = Path.cwd() / ".cursor-loop" / "last_verify.json"
    msg = "Cursor Loop validation: run `python3 -m cursor_loop verify`."
    if verify.exists():
        data = json.loads(verify.read_text(encoding="utf-8"))
        msg = f"Last verify result={data.get('result')} failures={data.get('failure_count')}"
    print(json.dumps({"additional_context": msg}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
}


HOOKS_JSON = {
    "version": 1,
    "hooks": {
        "preToolUse": [{"command": ".cursor/hooks/pre_task.py", "matcher": "Shell|Task", "timeout": 15}],
        "postToolUse": [{"command": ".cursor/hooks/post_task.py", "matcher": "Shell|Task|Write", "timeout": 15}],
        "postToolUseFailure": [{"command": ".cursor/hooks/failure.py", "timeout": 15}],
        "stop": [{"command": ".cursor/hooks/stop.py", "timeout": 15, "loop_limit": 3}],
        "subagentStop": [{"command": ".cursor/hooks/loop_continue.py", "timeout": 15, "loop_limit": 5}],
        "beforeSubmitPrompt": [
            {"command": ".cursor/hooks/research.py", "matcher": "UserPromptSubmit", "timeout": 10},
            {"command": ".cursor/hooks/validation.py", "matcher": "UserPromptSubmit", "timeout": 10},
        ],
    },
}


def write_rules() -> None:
    rules_dir = CURSOR / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    for name, body in RULES.items():
        (rules_dir / f"{name}.mdc").write_text(body.strip() + "\n", encoding="utf-8")


def write_skills() -> None:
    for name, (desc, body) in SKILLS.items():
        skill_dir = CURSOR / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        content = f"""---
name: {name}
description: {desc} Use when working with Cursor Loop Engineering {name.replace('-', ' ')}.
---

{body.strip()}
"""
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")


def write_agents() -> None:
    agents_dir = CURSOR / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    for name, (readonly, desc, body) in AGENTS.items():
        content = f"""---
name: {name}
description: {desc} Use when the user needs the {name} role in Cursor Loop Engineering.
model: inherit
readonly: {"true" if readonly else "false"}
---

You are the Cursor Loop Engineering **{name}** agent.

{body}

Authority order: project rules → skills → runtime controllers → CLI (`python3 -m cursor_loop`).
Never fabricate evidence. Prefer durable state under `.cursor-loop/`.
"""
        (agents_dir / f"{name}.md").write_text(content, encoding="utf-8")


def write_hooks() -> None:
    import json

    hooks_dir = CURSOR / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (CURSOR / "hooks.json").write_text(json.dumps(HOOKS_JSON, indent=2) + "\n", encoding="utf-8")
    for name, body in HOOKS.items():
        path = hooks_dir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | 0o111)


def write_templates_and_examples() -> None:
    templates = CURSOR / "templates"
    templates.mkdir(parents=True, exist_ok=True)
    (templates / "task.json").write_text(
        '{\n  "task_id": "T0000",\n  "mission": "",\n  "status": "READY",\n  "worker_role": "developer",\n  "dependencies": [],\n  "acceptance_criteria": []\n}\n',
        encoding="utf-8",
    )
    (templates / "loop_state.json").write_text(
        '{\n  "loop_id": "LOOP-V1",\n  "iteration": 0,\n  "retry_budget": 5,\n  "retries_used": 0,\n  "disposition": "IDLE"\n}\n',
        encoding="utf-8",
    )
    examples = CURSOR / "examples"
    examples.mkdir(parents=True, exist_ok=True)
    (examples / "verify-flow.md").write_text(
        "# Verify Flow\n\n```bash\npython3 -m cursor_loop install .\npython3 -m cursor_loop bootstrap\npython3 -m cursor_loop verify\npython3 -m cursor_loop status\n```\n",
        encoding="utf-8",
    )


def main() -> None:
    CURSOR.mkdir(parents=True, exist_ok=True)
    write_rules()
    write_skills()
    write_agents()
    write_hooks()
    write_templates_and_examples()
    print(f"Generated Cursor assets under {CURSOR}")


if __name__ == "__main__":
    main()
