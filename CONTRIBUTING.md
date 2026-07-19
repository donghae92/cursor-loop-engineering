# Contributing to Cursor Loop Engineering

Thank you for improving the framework. This document explains how to propose changes, run checks locally, and align with project conventions.

## Prerequisites

- Python 3.9 or newer (3.11 recommended)
- Git
- A Cursor installation (for manual hook and agent validation)

## Local setup

```bash
git clone https://github.com/donghae92/cursor-loop-engineering.git
cd cursor-loop-engineering
pip install -e ".[dev]"
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
| Migrations | `sdk/migrations/` | Upgrade/rollback scripts |
| Runtime controllers | `runtime/cursor_loop_runtime/` | Use atomic JSON writes |
| Cursor rules | `.cursor/rules/*.mdc` | Front matter + policy content |
| Skills | `.cursor/skills/<name>/SKILL.md` | Runnable commands, no placeholders |
| Agents | `.cursor/agents/<name>.md` | Role boundaries, readonly flag |
| Hooks | `.cursor/hooks/*.py` + `.cursor/hooks.json` | Keep fast; executable bit + timeout required |
| Plugin manifest | `.cursor-plugin/plugin.json` | Keep in sync with `VERSION` |
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

5. **Update docs** when CLI behavior, hooks, or runtime contracts change.
6. **Add a CHANGELOG entry** for user-visible changes (new section or update the latest version notes).
7. **Open a pull request** using the PR template.

## Coding standards

- Target Python 3.9+ syntax compatible with CI.
- Use `write_json_atomic` from `cursor_loop_runtime.models` for JSON persistence.
- CLI handlers return structured JSON and meaningful exit codes (`0`, `3`, `4`, `5`).
- Do not fabricate evidence, hashes, or test results.
- Prefer controllers and `cle` commands over ad-hoc one-off scripts.
- Do not redesign the frozen layout (`.cursor/`, `runtime/`, `sdk/`).

## Architecture freeze

Canonical Cursor assets live under `.cursor/`. Local plugin install may materialize root component directories for Cursor marketplace loading. Do not reintroduce dual hand-maintained source trees.

## Pull requests

- Keep PRs focused and reviewable.
- Include verification evidence (`cle verify`, `pytest`) in the PR body when changing runtime or installer behavior.
- Security-sensitive changes should reference SECURITY.md reporting channels when relevant.
