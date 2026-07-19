# Cursor Loop Engineering

Production-ready, **generic** Cursor engineering framework for any repository.

Install merge-safe `.cursor/` assets and a durable `.cursor-loop/` runtime. Coordinate verification, regression (L1–L8), repair, and release through a Python CLI—without project-specific or proprietary logic.

## Repository structure

```text
.cursor/          # Canonical Cursor assets (rules, skills, agents, hooks, commands)
runtime/          # Loop, scheduler, regression, evidence, memory controllers
sdk/              # CLI + installer + migrations
docs/             # Framework documentation
examples/         # Generic stack install examples
tests/            # Automated verification
scripts/          # Entrypoints (cle, install helper)
.github/          # CI and release workflows
```

## Quick start

```bash
git clone https://github.com/donghae92/cursor-loop-engineering.git
cd cursor-loop-engineering
pip install -e ".[dev]"

cle bootstrap --self
cle verify
```

Install into another project (no manual edits):

```bash
cle install /path/to/your-project
cle verify --path /path/to/your-project
cle update --path /path/to/your-project
cle doctor --path /path/to/your-project --repair
```

Install as a local Cursor plugin:

```bash
cle plugin-validate --self
cle plugin-install
```

## CLI

| Command | Purpose |
|---------|---------|
| `install [target]` | Merge-safe install into empty/existing/monorepo projects |
| `bootstrap [--path \| --self]` | Initialize `.cursor-loop/` runtime memory |
| `verify [--path]` | Rules, skills, agents, hooks, runtime, regression L1–L8, evidence |
| `doctor [--path] [--repair]` | Diagnose and optionally repair |
| `loop [--status \| --once]` | Localize → repair → retest loop |
| `status [--path]` | Versions, detection, runtime, upgrade plan |
| `update` / `repair` / `remove` | Lifecycle management |
| `export` / `import` / `rollback` / `release` | Packaging and migrations |
| `plugin-validate` / `plugin-install` / `plugin-update` / `plugin-remove` | Local plugin lifecycle |

Exit codes: `0` success, `3` loop stop disposition, `4` gate failure, `5` unexpected error.

## Features

- **Generic only** — no proprietary or product-specific logic
- **Evidence-first** — confidence is never evidence; claims need durable artifacts
- **Regression L1–L8** — schema, hash, provenance, semantic, temporal, dependency, representative, boot
- **Loop-aware** — failed sections localize, attempt deterministic repair, then continue or stop
- **Cursor-native** — assets under `.cursor/`; optional local plugin materialization for `/add-plugin`

## Documentation

- [docs/README.md](docs/README.md)
- [Installation](docs/installation.md)
- [Architecture](docs/architecture.md)
- [Plugin installation](docs/plugin-installation.md)
- [Compatibility](docs/compatibility-guide.md)

## License

MIT
