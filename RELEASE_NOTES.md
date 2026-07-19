# Release Notes — Cursor Loop Engineering v2.0.0

**Status:** Release Candidate  
**Date:** 2026-07-20  
**Tag intent:** `v2.0.0`

## Highlights

- Production Cursor plugin layout: root `rules/`, `skills/`, `agents/`, `commands/`, `hooks/`, plus `.cursor/` project-install mirror
- Runtime under `runtime/`; CLI/installer under `sdk/`
- First-class Cursor plugin packaging and local install
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

- Plugin assets follow Cursor conventions at repository root (`rules/`, `skills/`, `agents/`, `commands/`, `hooks/`).
- `.cursor/` remains the project-install mirror for consumer repositories.
- Installer package lives under `sdk/cursor_loop_install/`; migrations under `sdk/migrations/`.

## Verification

See [RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md) for gate evidence and known limitations.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history.
