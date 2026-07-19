# Loop engineering guide

Cursor Loop Engineering treats failed verification gates as **localized repair loops** with explicit stop conditions. This guide explains dispositions, retry budgets, and operator workflows.

## Core loop policy

From `loop-policy.mdc`:

```
Failed gate → localize → repair → re-validate → re-regress → recompute disposition
```

Continue only while all of the following exist:

- A concrete failure
- A corrective action
- New evidence
- Remaining retry budget
- Measurable progress

Otherwise stop with `SAFE_STOP` or `MANUAL_REVIEW`.

## State machine

Loop state persists in `.cursor-loop/loop_state.json`:

| Field | Meaning |
|-------|---------|
| `iteration` | Loop tick count |
| `section_id` | Active failed section |
| `retry_budget` | Max retries (default 5) |
| `retries_used` | Consumed retries |
| `last_gate` | Last gate name (e.g., verify regress) |
| `last_result` | `PASS` or `FAIL` |
| `disposition` | `IDLE`, `CONTINUE`, `SAFE_STOP`, `MANUAL_REVIEW` |
| `last_failure_fingerprint` | Hash of gate + failures |
| `identical_failure_count` | Repeated same fingerprint |

## Dispositions

| Disposition | Set when | Operator action |
|-------------|----------|-----------------|
| `IDLE` | Last gate passed | Normal development |
| `CONTINUE` | Failure with budget left | Run repair, fix root cause, `loop --once` |
| `SAFE_STOP` | Same fingerprint ≥ 3 times | Stop automation; investigate contradiction |
| `MANUAL_REVIEW` | `retries_used > retry_budget` | Human triage required |

CLI exit code `3` indicates `SAFE_STOP` or `MANUAL_REVIEW` after `loop --once`.

## Operator workflow

### 1. Detect failure

```bash
python3 -m cursor_loop verify
# or inspect last run
cat .cursor-loop/runtime/last_verify.json
```

### 2. Diagnose

```bash
python3 -m cursor_loop doctor
python3 -m cursor_loop status
```

Review `failures` array in verify JSON and recent events in status output.

### 3. Repair

```bash
python3 -m cursor_loop repair
```

Repair fixes hook permissions, recreates missing runtime files, and re-runs verify.

For logical failures (regression, missing assets):

```bash
python3 -m cursor_loop update   # refresh .cursor assets
# fix project-specific issue
python3 -m cursor_loop verify
```

### 4. Advance loop

```bash
python3 -m cursor_loop loop --once
python3 -m cursor_loop loop --status   # inspect without advancing
```

`LoopController.run_once()` reads `last_verify.json`, updates disposition, and appends decisions to `decision_history.jsonl`.

### 5. Release (optional)

Only after verify PASS:

```bash
python3 -m cursor_loop release
```

Creates a checkpoint under `.cursor-loop/checkpoints/` and transitions state to `READY_FOR_RELEASE`.

## Failure fingerprints

Identical failures hash gate name + sorted failure messages. Three identical hashes trigger `SAFE_STOP` to prevent infinite agent loops — a governance guard, not a bug.

To break a SAFE_STOP:

1. Change something material (fix root cause or baseline).
2. Re-run verify to get a new failure set or PASS.
3. Run `loop --once` to reset disposition logic.

## Skills and agents

| Role | Skill / agent | Use |
|------|---------------|-----|
| Implement fix | `developer` + `loop` skill | Minimal code change |
| Validate | `qa` + `validation` skill | Independent verify |
| Regress | `regression` + `regression-check` | Baseline integrity |
| Repair runtime | `runtime-repair` skill | Degraded `.cursor-loop/` |
| Stop gate | `ceo` agent | Mission-level stop |

## Evidence and quarantine

Ambiguous outputs go to `.cursor-loop/quarantine/` per `evidence-policy.mdc`. Do not promote claims without file paths, hashes, or CLI JSON.

## Scheduler integration

`Scheduler.run()` executes during verify and bootstrap. Task queue files:

- `.cursor-loop/task_queue.jsonl`
- `.cursor-loop/backlog.jsonl`

Use the `scheduler` skill for queue inspection.

## Anti-patterns

- Re-running verify without changing anything expecting different results
- Skipping verify before `release`
- Writing loop state by hand instead of using CLI controllers
- Fabricating PASS in agent text while `last_verify.json` says FAIL

## Related

- [Architecture](architecture.md)
- [Validation policy](../.cursor/rules/validation-policy.mdc)
- [Quick start](quick-start.md)
