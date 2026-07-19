# Contributing to Cursor Loop Engineering

Thank you for improving the framework. This document explains how to propose changes, run checks locally, and align with project conventions.

## Prerequisites

- Python 3.10 or newer
- Git
- A Cursor installation (for manual hook and agent validation)

## Local setup

```bash
git clone https://github.com/your-org/cursor-loop-engineering.git
cd cursor-loop-engineering
pip install -e ".[dev]"  # or: pip install -e .
python3 -m cursor_loop bootstrap --self
python3 -m cursor_loop doctor
python3 -m cursor_loop verify
```

Run tests:

```bash
pytest
```

## What to change where

| Area | Location | Notes |
|------|----------|-------|
| CLI commands | `sdk/cursor_loop/cli.py` | JSON stdout, explicit exit codes |
| Install logic | `sdk/cursor_loop_install/` | Asset copy + manifest hashes |
| Runtime controllers | `runtime/cursor_loop_runtime/` | Use atomic JSON writes |
| Cursor rules | `.cursor/rules/*.mdc` | Front matter + policy content |
| Skills | `.cursor/skills/<name>/SKILL.md` | Runnable commands, no placeholders |
| Agents | `.cursor/agents/<name>.md` | Role boundaries, readonly flag |
| Hooks | `.cursor/hooks/*.py` + `hooks.json` | Keep fast; executable bit required |
| Derived state | `.cursor-loop/` only | Never commit secrets here |
| User docs | `docs/` | Update when CLI or contracts change |

## Development workflow

1. **Open an issue** for substantial features or breaking changes before large PRs.
2. **Create a branch** from `main`: `feat/short-description` or `fix/short-description`.
3. **Make minimal diffs** — one logical change per commit when possible.
4. **Run gates locally**:

   ```bash
   python3 -m cursor_loop verify
   pytest
   ```

5. **Update docs** when CLI behavior, hooks, or runtime contracts change (see `documentation-policy` rule).
6. **Add a CHANGELOG entry** under `[Unreleased]` for user-visible changes.
7. **Open a pull request** using the PR template.

## Coding standards

- Target Python 3.10+ syntax.
- Use `write_json_atomic` from `cursor_loop_runtime.models` for JSON persistence.
- CLI handlers return structured JSON and meaningful exit codes (`0`, `3`, `4`, `5`).
- Do not fabricate evidence, hashes, or test results.
- Prefer controllers and `cle` commands over ad-hoc one-off scripts.

## Rules for Cursor assets

### Rules (`.mdc`)

- Include YAML front matter with `description`.
- Set `alwaysApply: true` only for cross-cutting policies.
- Use `globs` for scoped rules (e.g., Python under `runtime/`).

### Skills

- Name matches directory: `.cursor/skills/<name>/SKILL.md`.
- First lines: `name` and `description` in front matter.
- Include real shell commands agents can run.

### Agents

- Define authority boundaries (read-only vs implement).
- Reference CLI and `.cursor-loop/` paths explicitly.

### Hooks

- Read JSON from stdin; print JSON to stdout.
- Finish within configured timeouts in `hooks.json`.
- Mark scripts executable (`chmod +x`); `cle repair` fixes this automatically.

## Verification expectations

`cle verify` checks:

- Required `.cursor/` directories and files
- All bundled rules, skills, agents, and hooks
- Regression and evidence controllers
- Scheduler run

A failing gate blocks `cle release`. Fix with `cle repair` or address the reported failure.

## Pull request checklist

- [ ] `python3 -m cursor_loop verify` passes
- [ ] `pytest` passes (or documents why tests are N/A)
- [ ] Docs updated for user-visible changes
- [ ] CHANGELOG updated
- [ ] No secrets or credentials committed
- [ ] Hook scripts remain executable

## Code of conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions

Open a [GitHub Discussion](https://github.com/your-org/cursor-loop-engineering/discussions) or file an issue labeled `question`.
