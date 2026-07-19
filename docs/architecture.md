# Architecture

## Layers

```text
Rules → Skills → Agents → Hooks → Runtime Controllers → CLI
```

## Canonical layout

| Path | Authority |
|------|-----------|
| `.cursor/` | Only installable Cursor assets |
| `.cursor-loop/` | Only derived runtime memory |
| `runtime/` | Loop, scheduler, regression, evidence, memory |
| `sdk/cursor_loop/` | CLI |
| `sdk/cursor_loop_install/` | Install, verify, doctor, plugin, export |
| `sdk/migrations/` | Versioned upgrades |

## Non-goals

- No proprietary or product-specific reconstruction logic
- No dual source-of-truth trees for rules/skills/agents in git
- No confidence-as-evidence

## Controllers

- **Memory** — durable state, events, decisions, timings
- **Scheduler** — dependency-aware task queue
- **Regression** — L1–L8 gates
- **Evidence** — allow-listed evidence classes + artifact checks
- **Loop** — localize → repair → disposition
- **Checkpoint** — restore points for release/repair
