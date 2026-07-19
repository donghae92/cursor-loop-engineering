# Plugin Installation Guide

## Option A — Local Cursor plugin

From this repository:

```bash
pip install -e ".[dev]"
python -m cursor_loop plugin-validate --self
python -m cursor_loop plugin-install
# optional: install into a custom local-plugins directory
python -m cursor_loop plugin-install --target /path/to/plugins/local
```

Cursor discovers the plugin under:

`~/.cursor/plugins/local/cursor-loop-engineering`

Enable it from Cursor’s Plugins / Marketplace UI.

Upgrade later:

```bash
python -m cursor_loop plugin-update
```

Rollback the local plugin by restoring the backup directory created next to the install, or reinstall a previous release tag.

## Option B — Install into a project (no plugin UI required)

```bash
python -m cursor_loop install /path/to/your/project
python -m cursor_loop verify --path /path/to/your/project
```

This copies rules/skills/agents/hooks/commands into the project’s `.cursor/` with merge-safe backups.

## Option C — GitHub Release archive

```bash
python -m cursor_loop export --output dist
python -m cursor_loop import dist/cursor-loop-engineering-1.2.0.tar.gz --target /path/to/project
```

## Verification

```bash
python -m cursor_loop plugin-validate --self
python -m cursor_loop verify --path .
python -m cursor_loop doctor --path . --repair
```
