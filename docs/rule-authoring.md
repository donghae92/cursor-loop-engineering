# Rule authoring

Rules are persistent instructions Cursor applies to agents. In Cursor Loop Engineering, rules live as **Markdown with YAML front matter** in `.cursor/rules/*.mdc`.

## File format

```markdown
---
description: Short summary shown in Cursor rule picker
alwaysApply: true
globs: "**/*.py"
---

# Rule title

Rule body in Markdown.
```

## Front matter fields

| Field | Purpose |
|-------|---------|
| `description` | Human-readable summary (required for discoverability) |
| `alwaysApply` | `true` = every session; `false` = opt-in or glob-scoped |
| `globs` | Optional path patterns when `alwaysApply` is false |

Example scoped rule (from framework `coding-standards.mdc`):

```yaml
---
description: Coding standards for Cursor Loop Engineering Python modules
globs: "**/{runtime,sdk,install,scripts,tests}/**/*.py"
alwaysApply: false
---
```

## Policy vs project rules

### Framework policies (shipped)

Always-on policies installed with the framework:

| Rule file | Scope |
|-----------|-------|
| `architecture.mdc` | Layer boundaries, `.cursor-loop/` writes |
| `coding-standards.mdc` | Python in sdk/runtime/install |
| `validation-policy.mdc` | Independent verification |
| `regression-policy.mdc` | Baseline levels L1–L8 |
| `evidence-policy.mdc` | Citations, quarantine |
| `loop-policy.mdc` | Stop dispositions |
| `research-policy.mdc` | Read-only exploration |
| `review-policy.mdc` | Reviewer boundaries |
| `release-policy.mdc` | Release gates |
| `safety-policy.mdc` | Secrets, destructive ops |
| `performance-policy.mdc` | Hook timing |
| `documentation-policy.mdc` | Docs when contracts change |

### Project rules (your code)

Add after install without removing framework policies:

```bash
# .cursor/rules/my-app.mdc
---
description: API conventions for our REST services
globs: "services/**/*.ts"
alwaysApply: false
---

# REST conventions

- Use OpenAPI-generated types.
- Run `npm test` before requesting review.
```

Merge behavior: `install` copies framework files; project-specific rules coexist in the same directory.

## Writing effective rules

1. **One concern per file** — Easier to review and disable.
2. **Imperative voice** — "Run verify after infrastructure changes."
3. **Point to CLI** — `python3 -m cursor_loop verify` not vague "validate."
4. **Fail closed** — Prefer blocking unsafe actions (see `safety-policy.mdc`).
5. **Avoid duplication** — Link to docs/skills for long procedures.

## Verify integration

Bundled rule filenames are checked by `cle verify`. If you fork the framework and add required rules, update the `rule_names` list in `sdk/cursor_loop/cli.py`.

## Regression

Rule files participate in L2 hash regression (`RegressionController`). Changing a bundled rule changes baseline hashes — record intent in CHANGELOG.

## Related

- [Skill authoring](skill-authoring.md)
- [Architecture](architecture.md)
- [Documentation policy](../.cursor/rules/documentation-policy.mdc)
