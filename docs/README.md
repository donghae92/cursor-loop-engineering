# Cursor Loop Engineering Documentation

Welcome to the documentation for **Cursor Loop Engineering** — a reusable AI engineering framework for any Cursor project.

## Getting started

| Document | Description |
|----------|-------------|
| [Quick start](quick-start.md) | Install, bootstrap, verify in five minutes |
| [Installation](installation.md) | pip install, path setup, CI integration |
| [Architecture](architecture.md) | Layers, controllers, runtime memory |

## Authoring guides

| Document | Description |
|----------|-------------|
| [Rule authoring](rule-authoring.md) | Write `.cursor/rules/*.mdc` policies |
| [Skill authoring](skill-authoring.md) | Write `.cursor/skills/*/SKILL.md` workflows |
| [Subagent authoring](subagent-authoring.md) | Define `.cursor/agents/*.md` roles |
| [Hook authoring](hook-authoring.md) | Extend `.cursor/hooks/` lifecycle scripts |

## Operations

| Document | Description |
|----------|-------------|
| [Loop engineering guide](loop-engineering-guide.md) | Failed-section loops, dispositions, repair |
| [Examples](examples.md) | Index of per-stack example READMEs |
| [Migration guide](migration-guide.md) | Upgrade paths and asset updates |

## CLI reference

All commands accept `--path` (default: current directory) unless noted.

```bash
python3 -m cursor_loop install [target]
python3 -m cursor_loop bootstrap [--self]
python3 -m cursor_loop verify
python3 -m cursor_loop doctor
python3 -m cursor_loop loop [--status | --once]
python3 -m cursor_loop status
python3 -m cursor_loop update
python3 -m cursor_loop repair
python3 -m cursor_loop release
```

Equivalent invocations:

```bash
./scripts/cle <command>
cle <command>   # after pip install -e .
```

## Key paths

| Path | Purpose |
|------|---------|
| `.cursor/` | Installable rules, skills, agents, hooks |
| `.cursor-loop/` | Derived runtime memory (JSON / JSONL) |
| `sdk/cursor_loop/` | CLI package |
| `runtime/cursor_loop_runtime/` | Controllers |
| `install/install.py` | Asset copy and manifest |

## Policies (in-repo)

Framework policies ship as Cursor rules under `.cursor/rules/`:

- `architecture.mdc` — Layer boundaries
- `loop-policy.mdc` — Loop stop conditions
- `validation-policy.mdc` — Gate requirements
- `regression-policy.mdc` — Baseline levels
- `evidence-policy.mdc` — Evidence requirements
- `safety-policy.mdc` — Destructive action guards

Read these in Cursor or in the repository when extending the framework.

## External links

- [Repository README](../README.md)
- [Contributing](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)
- [Security](../SECURITY.md)
