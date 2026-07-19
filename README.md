# Cursor Loop Engineering

Reusable AI engineering framework for **any** Cursor project. Cursor Loop Engineering installs durable rules, skills, agents, and hooks into your repository, then coordinates verification, regression, repair, and release through a Python CLI and runtime memory under `.cursor-loop/`.

## Why use it

- **Portable** — Install into Android, Python, Node, Rust, Flutter, or any other stack.
- **Evidence-first** — Gates, hashes, and regression levels block release on unknown or failed checks.
- **Loop-aware** — Failed sections drive localized repair with retry budgets and safe stop dispositions.
- **Cursor-native** — Assets live in `.cursor/`; agents and hooks integrate with Cursor's agent runtime.

## Quick start

```bash
git clone https://github.com/donghae92/cursor-loop-engineering.git
cd cursor-loop-engineering

# Editable install (recommended for development)
pip install -e ".[dev]"

# Or run without install
./scripts/cle bootstrap --self
./scripts/cle verify
```

Install into another project:

```bash
python3 -m cursor_loop install /path/to/your-project
python3 -m cursor_loop verify --path /path/to/your-project
python3 -m cursor_loop update --path /path/to/your-project
python3 -m cursor_loop doctor --path /path/to/your-project --repair
```

See [docs/installation.md](docs/installation.md) and [docs/quick-start.md](docs/quick-start.md).

## CLI

| Command | Purpose |
|---------|---------|
| `install [target]` | Merge-safe install into empty/existing/monorepo projects |
| `bootstrap [--path \| --self]` | Initialize `.cursor-loop/` runtime memory |
| `verify [--path]` | Check rules, skills, agents, hooks, runtime, regression, evidence, memory |
| `doctor [--path] [--repair]` | Diagnose and optionally repair installation |
| `loop [--status \| --once]` | Advance or inspect the engineering loop |
| `status [--path]` | Show versions, detection, runtime, upgrade plan |
| `update [--path] [--force]` | Incremental update preserving customizations |
| `repair [--path]` | Repair missing assets and re-verify |
| `remove [--path] [--purge-runtime]` | Remove managed framework assets |
| `export [--output]` | Package framework for GitHub Releases |
| `import ARCHIVE [--target]` | Install from a release archive |
| `rollback [--migration-id]` | Roll back the last migration |
| `release [--path]` | Verify, checkpoint, and export release assets |

Invocation options (equivalent after install):

```bash
python3 -m cursor_loop <command>
./scripts/cle <command>
cle <command>   # after pip install -e .
```

All commands emit JSON to stdout and use exit codes: `0` success, `3` loop stop disposition, `4` gate failure, `5` unexpected error.

## Features

### Layered architecture

Rules → Skills → Agents → Hooks → Runtime Controllers → CLI

Each layer has a clear boundary. Derived state is written only under `.cursor-loop/`. Installable Cursor assets live under `.cursor/`.

### Runtime memory (`.cursor-loop/`)

| File | Role |
|------|------|
| `state.json` | Framework health and phase |
| `loop_state.json` | Loop iteration, disposition, retry budget |
| `performance.json` | Timing aggregates for validate/regress |
| `task_queue.jsonl` / `backlog.jsonl` | Scheduled work |
| `regression_history.jsonl` | Regression run records |
| `decision_history.jsonl` | Gate and loop decisions |
| `evidence_log.jsonl` | Evidence checks |
| `events.jsonl` | Structured event log |
| `install_manifest.json` | Installed asset hashes |
| `checkpoints/` | Release and bootstrap checkpoints |
| `quarantine/` | Ambiguous outputs pending review |

### Cursor assets (`.cursor/`)

| Directory | Contents |
|-----------|----------|
| `rules/` | Always-on and scoped policies (`.mdc`) |
| `skills/` | Task workflows (`SKILL.md` per skill) |
| `agents/` | Role definitions for subagents |
| `hooks/` | Python hook scripts + `hooks.json` |
| `templates/` | Loop and task JSON templates |
| `examples/` | In-repo usage examples |

### Built-in agents

`ceo`, `manager`, `planner`, `researcher`, `developer`, `reviewer`, `qa`, `regression`, `release`, `documentation`

### Regression levels

L1 schema through L8 boot (extensible via `RegressionController`). Baselines include artifact id, version, and hash — no floating baselines.

## Repository structure

```
cursor-loop-engineering/
├── .cursor/                 # Framework Cursor assets (copied on install)
├── .cursor-loop/            # Runtime memory (created by bootstrap; gitignored in targets)
├── docs/                    # Documentation
├── examples/                # Per-stack install guides
├── install/                 # Install module
├── runtime/
│   └── cursor_loop_runtime/ # Controllers (loop, memory, regression, …)
├── sdk/
│   └── cursor_loop/         # CLI entrypoint
├── scripts/
│   └── cle                  # Convenience launcher
├── pyproject.toml
└── tests/                   # pytest suite
```

## Documentation

- [Documentation index](docs/README.md)
- [Quick start](docs/quick-start.md)
- [Installation](docs/installation.md)
- [Architecture](docs/architecture.md)
- [Loop engineering guide](docs/loop-engineering-guide.md)
- [Examples by stack](docs/examples.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities per [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) — see [CHANGELOG.md](CHANGELOG.md) for release history.
