# Marketplace description

**Cursor Loop Engineering** is a production Cursor engineering framework for any repository.

## Highlights

- Merge-safe install into empty, existing, and monorepo projects
- Canonical `.cursor/` rules, skills, agents, hooks, and slash commands
- Runtime controllers for loop, scheduler, regression L1–L8, and evidence
- Local plugin install under `~/.cursor/plugins/local/`

## Install

```bash
pip install -e .
cle plugin-validate --self
cle plugin-install
```

Or project install:

```bash
cle install /path/to/project
cle verify --path /path/to/project
```

## Requirements

- Python 3.9+ (3.11 recommended)
- Cursor IDE with hooks/plugins support

Generic framework only — no proprietary project adapters.
