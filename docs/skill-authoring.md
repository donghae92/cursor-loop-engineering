# Skill authoring

Skills teach Cursor agents **how** to perform recurring tasks. Each skill is a directory with a `SKILL.md` file under `.cursor/skills/`.

## File location

```
.cursor/skills/
└── my-skill/
    └── SKILL.md
```

The directory name should match the skill `name` in front matter.

## Minimal template

```markdown
---
name: my-skill
description: One-line summary of when to use this skill. Be specific so agents discover it.
---

# My Skill

## When to use

Describe triggers: e.g., "after infrastructure changes" or "when verify fails."

## Commands

\`\`\`bash
python3 -m cursor_loop verify
python3 -m cursor_loop status
\`\`\`

## Steps

1. Run verify and capture `last_verify.json`.
2. If FAIL, run repair and re-verify.
3. Record decision in `.cursor-loop/decision_history.jsonl` via CLI only.

## Evidence

Cite paths and command output — never fabricate hashes or pass results.
```

## Front matter rules

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Lowercase, hyphenated; matches directory |
| `description` | Yes | Shown in skill discovery; include trigger phrases |

Optional fields follow Cursor skill conventions as they evolve; keep the file valid Markdown after the closing `---`.

## Bundled skills (v1.0.0)

These ship with the framework and are verified by `cle verify`:

| Skill | Purpose |
|-------|---------|
| `architecture-review` | Review against framework layers |
| `repository-analysis` | Structure and dependency survey |
| `bootstrap` | Initialize runtime memory |
| `hash-audit` | Compare install manifest hashes |
| `memory` | Inspect `.cursor-loop/` state |
| `loop` | Advance engineering loop |
| `scheduler` | Task queue sync |
| `report` | Structured reports from runtime |
| `release` | Release checkpoint workflow |
| `research` | Read-only exploration |
| `validation` | Run verify/doctor |
| `regression-check` | Regression controller |
| `graph-builder` | Dependency graphs |
| `runtime-repair` | Diagnose degraded runtime |

When adding a new bundled skill, update the skill list in `sdk/cursor_loop/cli.py` (`cmd_verify`) so verify enforces it.

## Content guidelines

1. **Runnable commands** — Use real `python3 -m cursor_loop` or project commands, not placeholders.
2. **Short sessions** — Skills should fit agent context limits; link to docs for depth.
3. **Evidence policy** — Align with `evidence-policy.mdc`: cite files, hashes, CLI JSON.
4. **No duplicate controllers** — Call CLI instead of reimplementing Python logic inline.
5. **Runtime writes** — Direct agents to `.cursor-loop/` for derived artifacts.

## Project-specific skills

After `cle install`, add skills under the target project's `.cursor/skills/`:

```bash
mkdir -p .cursor/skills/deploy-staging
```

Custom skills do not need to be listed in `cli.py` unless you fork the framework and extend verify.

## Testing a skill

1. Open the project in Cursor.
2. Prompt: "Use the my-skill skill to …"
3. Confirm the agent runs listed commands and respects rules.

Run verify after adding bundled skills:

```bash
python3 -m cursor_loop verify
```

## Related

- [Rule authoring](rule-authoring.md)
- [Subagent authoring](subagent-authoring.md)
- [Loop engineering guide](loop-engineering-guide.md)
