# Release Notes — Cursor Loop Engineering v2.0.0

**Status:** Release Candidate  
**Date:** 2026-07-20  
**Tag intent:** `v2.0.0`

## Highlights

- Production layout frozen: `.cursor/`, `runtime/`, `sdk/`, `docs/`, `examples/`, `tests/`, `scripts/`, `.github/`
- First-class Cursor plugin packaging with local install materialization
- Regression levels L1–L8 fully executed (not skipped)
- Loop localize → repair → retest with stop dispositions
- Merge-safe project installer with backups and migrations
- Hook timeouts and unsafe-pattern denials

## Install

### Project install

```bash
pip install -e .
cle install /path/to/project
cle verify --path /path/to/project
```

### Local Cursor plugin

```bash
cle plugin-validate --self
cle plugin-install
```

### From release archive

```bash
python -m cursor_loop import cursor-loop-engineering-2.0.0.tar.gz --target /path/to/project
python -m cursor_loop verify --path /path/to/project
```

## Upgrade

From 1.2.0:

```bash
cle update --path /path/to/project
```

Migration path: `1.0.0 → 1.1.0 → 1.2.0 → 2.0.0` via `sdk/migrations/`.

## Breaking changes

- Canonical Cursor assets live only under `.cursor/`
- Installer package moved to `sdk/cursor_loop_install/`
- Migrations moved to `sdk/migrations/`
- Root dual mirrors of rules/skills/agents/hooks are no longer maintained in source

## Verification

See [RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md) for gate evidence and known limitations.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history.
