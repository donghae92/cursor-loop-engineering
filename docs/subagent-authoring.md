# Subagent authoring

Subagents (Cursor **agents**) are role definitions stored as Markdown with YAML front matter in `.cursor/agents/*.md`. They specialize multi-step work while staying within framework boundaries.

## File location

```
.cursor/agents/
├── developer.md
├── reviewer.md
└── my-custom-agent.md
```

## Minimal template

```markdown
---
name: my-custom-agent
description: When the user needs X, use this agent. Include trigger phrases.
model: inherit
readonly: false
---

You are the **my-custom-agent** role for Cursor Loop Engineering.

## Authority

- Follow project rules, then skills, then runtime controllers.
- Use `python3 -m cursor_loop verify` after infrastructure edits.

## Boundaries

- Write derived state only under `.cursor-loop/`.
- Do not fabricate evidence or test results.

## Workflow

1. Read relevant skill (e.g., validation).
2. Implement minimal change.
3. Run verify and report JSON result.
```

## Front matter fields

| Field | Typical value | Meaning |
|-------|---------------|---------|
| `name` | `developer` | Agent identifier |
| `description` | One sentence | Discovery text for routing |
| `model` | `inherit` | Use parent conversation model |
| `readonly` | `true` / `false` | Block write tools when true |

Use `readonly: true` for reviewers, researchers, and QA roles that must not edit source.

## Bundled agents (v1.0.0)

| Agent | Role | Readonly |
|-------|------|----------|
| `ceo` | Mission gates and stop dispositions | false |
| `manager` | Queue advancement and verification cycles | false |
| `planner` | Task DAG design; never executes | true |
| `researcher` | Read-only repository research | true |
| `developer` | Implements changes | false |
| `reviewer` | Independent review | true |
| `qa` | Runs verify/doctor | false |
| `regression` | Regression baselines | false |
| `release` | Release checkpoints | false |
| `documentation` | Docs and examples | false |

Verify checks for all ten files (`cmd_verify` in `cli.py`).

## Role separation

Follow `review-policy.mdc`:

- **Reviewers** report Critical / Suggestion / Nice-to-have with evidence.
- **Reviewers do not** author replacement implementations inside the review.
- **Developers** implement; **QA** validates independently.

## Invoking agents

In Cursor, users launch subagents by name or description. Write descriptions that match natural prompts:

```yaml
description: Implements framework and project-derived changes. Use when the user needs the developer role in Cursor Loop Engineering.
```

## Hook integration

`subagentStop` runs `.cursor/hooks/loop_continue.py` to continue engineering loops after subagent completion (see [Hook authoring](hook-authoring.md)).

## Adding a custom agent

1. Create `.cursor/agents/my-agent.md` in the target project.
2. Set clear readonly boundaries.
3. Reference skills and CLI commands explicitly.

Custom agents are not required in `cli.py` unless you extend verify in a fork.

## Related

- [Skill authoring](skill-authoring.md)
- [Hook authoring](hook-authoring.md)
- [Loop engineering guide](loop-engineering-guide.md)
