# Marketplace description

**Cursor Loop Engineering** is a production Cursor plugin and engineering framework for any repository.

## What it provides

- **Rules** — always-on engineering policies (evidence, regression, loop, safety, release)
- **Skills** — bootstrap, validate, loop, regression, release, repair, and more
- **Agents** — ceo, manager, planner, researcher, developer, qa, regression, reviewer, documentation, release
- **Hooks** — pre/post tool, validation, failure, stop, and research hooks with timeouts and unsafe-pattern denial
- **Commands** — `cle-verify`, `cle-status`, `cle-repair`, `cle-loop`, `cle-install`, `cle-update`
- **Runtime + CLI** — merge-safe install/update, regression L1–L8, evidence checks, loop repair
- **MCP** — `mcp.json` present (empty servers by default; extend per project)

## Install (local plugin)

```bash
pip install -e .
cle plugin-validate --self
cle plugin-install
```

Enable under Cursor local plugins:

`~/.cursor/plugins/local/cursor-loop-engineering`

## Install (project)

```bash
cle install /path/to/project
cle verify --path /path/to/project
```

## Requirements

- Python 3.9+ (3.11 recommended)
- Cursor IDE with plugins/hooks support

## Submission notes

- Single-plugin repository with `.cursor-plugin/plugin.json`
- Logo: `assets/logo.svg`
- Canonical source assets live under `.cursor/`; local plugin install materializes marketplace-conventional root component directories
- License: MIT
- Publish review: https://cursor.com/marketplace/publish

Generic framework only — no proprietary project adapters.
