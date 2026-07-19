# Architecture

Cursor Loop Engineering is organized as a **layered framework**. Each layer has a single responsibility and a strict write boundary.

## Layer diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Rules (.cursor/rules/*.mdc)                                │
│  Always-on and scoped policies for agents                   │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Skills (.cursor/skills/*/SKILL.md)                         │
│  Task workflows with runnable commands                      │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Agents (.cursor/agents/*.md)                               │
│  Role definitions for Cursor subagents                      │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Hooks (.cursor/hooks/*.py + hooks.json)                    │
│  Lifecycle guards around tool use and prompts               │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Runtime Controllers (runtime/cursor_loop_runtime/)         │
│  Memory, loop, scheduler, regression, evidence, checkpoints │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CLI (sdk/cursor_loop/cli.py)                               │
│  install · verify · loop · repair · release · …             │
└─────────────────────────────────────────────────────────────┘
```

**Authority order:** project rules → skills → runtime controllers → CLI.

Prefer `python3 -m cursor_loop` (or `cle`) over ad-hoc scripts that duplicate controller logic.

## Write boundaries

| Location | May write | Must not write |
|----------|-----------|----------------|
| `.cursor/` | Framework assets at install/update time | Derived runtime state |
| `.cursor-loop/` | All derived JSON/JSONL state | Source code |
| Project source | Application code (via agents) | Framework manifest without install |
| `sdk/` / `runtime/` | Framework implementation | Project-specific secrets |

Hooks and agents should direct derived artifacts to `.cursor-loop/` only (see `architecture.mdc` rule).

## Runtime controllers

Package: `runtime/cursor_loop_runtime/`

| Controller | Module | Responsibility |
|------------|--------|----------------|
| Memory | `memory_controller.py` | Ensure runtime files, event log, decisions |
| Loop | `loop_controller.py` | Gate results, retry budget, dispositions |
| Scheduler | `scheduler.py` | Task queue synchronization |
| Task queue | `task_queue.py` | Backlog and ready tasks |
| State machine | `state_machine.py` | Health phases (BOOTSTRAPPED → HEALTHY → …) |
| Regression | `regression_controller.py` | L1–L8 integrity checks |
| Evidence | `evidence_controller.py` | Evidence log consistency |
| Checkpoint | `checkpoint_manager.py` | Bootstrap and release snapshots |

Shared utilities live in `models.py`: atomic JSON writes, SHA-256 helpers, `WorkspacePaths`, `LoopState`, enums for disposition and task status.

## Runtime memory layout

Root: `.cursor-loop/` (created by `bootstrap`)

```
.cursor-loop/
├── state.json                 # phase, health, framework version
├── loop_state.json            # iteration, disposition, retry budget
├── performance.json           # validate/regress timing aggregates
├── task_queue.jsonl
├── backlog.jsonl
├── regression_history.jsonl
├── decision_history.jsonl
├── evidence_log.jsonl
├── events.jsonl
├── install_manifest.json      # SHA-256 of installed .cursor files
├── runtime/
│   └── last_verify.json       # Latest verify output
├── checkpoints/               # Named checkpoint directories
└── quarantine/                # Ambiguous outputs pending review
```

## CLI package

Root: `sdk/cursor_loop/`

- `cli.py` — Argument parser and command handlers
- `paths.py` — `framework_root()` discovery (three levels above `cli.py`)
- `__main__.py` — `python3 -m cursor_loop` entry

The CLI always prints JSON to stdout. Exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 3 | Loop disposition SAFE_STOP or MANUAL_REVIEW |
| 4 | Verify, doctor, or repair failure |
| 5 | Unexpected exception |

## Install pipeline

`install/install.py`:

1. Resolve target project directory
2. Copy `.cursor/hooks.json` and asset directories (`rules`, `skills`, `agents`, `hooks`, `templates`, `examples`)
3. `chmod +x` on hook scripts
4. `MemoryController.ensure()` on target
5. Write `install_manifest.json` with per-file SHA-256
6. Seed `AGENTS.md` if absent

`update` is implemented as `install --force`.

## Verification pipeline

`verify` runs sequential checks:

1. **Infrastructure** — Required `.cursor/` paths exist
2. **Rules** — Twelve bundled policy files present
3. **Skills** — Fourteen skill directories with `SKILL.md`
4. **Agents** — Ten agent markdown files
5. **Hooks** — Seven Python hooks registered in `hooks.json`
6. **Regression** — `RegressionController.run()`
7. **Evidence** — `EvidenceController.check()`
8. **Schedule** — `Scheduler.run()`

Results are written to `.cursor-loop/runtime/last_verify.json`. On failure, the state machine enters `REPAIRING`.

## Loop dispositions

From `loop_controller.py` and `loop-policy.mdc`:

| Disposition | When |
|-------------|------|
| `IDLE` | Last gate passed |
| `CONTINUE` | Failure with retry budget remaining |
| `SAFE_STOP` | Same failure fingerprint three times |
| `MANUAL_REVIEW` | Retry budget exhausted |

Flow: failed gate → localize → repair → re-validate → re-regress → recompute disposition.

## Hook lifecycle

Configured in `.cursor/hooks.json` (version 1):

| Hook event | Script | Purpose |
|------------|--------|---------|
| `preToolUse` | `pre_task.py` | Pre-shell/task guidance |
| `postToolUse` | `post_task.py` | Post-task reminders |
| `postToolUseFailure` | `failure.py` | Log failures |
| `stop` | `stop.py` | Session stop handling |
| `subagentStop` | `loop_continue.py` | Subagent loop continuation |
| `beforeSubmitPrompt` | `research.py`, `validation.py` | Prompt-time policy hints |

Keep hook scripts fast (10–15s timeouts).

## Regression levels

Documented in `regression-policy.mdc`:

- **L1** — Schema validation (`hooks.json` structure)
- **L2** — Hash integrity of rules and hooks
- **L3–L8** — Provenance, semantic, temporal, dependency, representative, boot (extensible)

Baselines require artifact id, version, and hash — no floating baselines.

## Extension points

1. **Project rules** — Add `.cursor/rules/my-project.mdc` after install (merge-safe)
2. **Project skills** — Add `.cursor/skills/my-skill/SKILL.md`
3. **Custom regression** — Extend `RegressionController` in a fork or wrapper
4. **CI** — Run `verify` on every PR (see `.github/workflows/ci.yml`)

## Related documents

- [Quick start](quick-start.md)
- [Loop engineering guide](loop-engineering-guide.md)
- [Installation](installation.md)
