# Plugin Compatibility Report

**Repository:** cursor-loop-engineering  
**Version:** 2.0.0  
**Date:** 2026-07-20  
**Reference:** [Cursor Plugins](https://cursor.com/docs/plugins) / [Plugins Reference](https://cursor.com/docs/reference/plugins)

## Summary

Migrated the existing repository to **current Cursor plugin conventions** without redesigning the engineering framework. Root component directories are now the plugin source of truth; `.cursor/` remains the project-install mirror.

## Components already compliant

| Component | Status | Notes |
|-----------|--------|-------|
| `.cursor-plugin/plugin.json` | Compliant (updated paths) | Required `name`; version, author, license, logo present |
| `mcp.json` | Compliant | Present (`mcpServers` empty by design) |
| `assets/logo.svg` | Compliant | Referenced by manifest |
| `README.md` | Compliant | Present |
| `CHANGELOG.md` | Compliant | Present |
| `LICENSE` | Compliant | MIT |
| `runtime/` / `sdk/` | Retained | Framework implementation unchanged in role |
| Tests / CI / release workflows | Retained | Continue to validate install + plugin gates |

## Components migrated

| Component | Before | After |
|-----------|--------|-------|
| Rules | `.cursor/rules/` only (manifest pointed here) | Root `rules/` + mirrored to `.cursor/rules/` |
| Skills | `.cursor/skills/` | Root `skills/` + mirror |
| Agents | `.cursor/agents/` | Root `agents/` + mirror |
| Commands | `.cursor/commands/` | Root `commands/` + mirror |
| Hooks | `.cursor/hooks.json` + `.cursor/hooks/*.py` | `hooks/hooks.json` with `./hooks/*` + scripts; project mirror uses `.cursor/hooks/` |
| Manifest paths | `./.cursor/...` | `./rules/`, `./skills/`, `./agents/`, `./commands/`, `./hooks/hooks.json` |
| `sync_plugin_layout` | Enforced `.cursor/` as canonical | Enforces **root convention** and mirrors into `.cursor/` |
| Installer `merger` | Read `.cursor/` only | Prefers root dirs, falls back to `.cursor/` |
| Local plugin install | Materialized root dirs from `.cursor/` | Copies already-conventional root tree |

## Components intentionally retained (not removed)

| Component | Why |
|-----------|-----|
| `.cursor/` | Required for project installs and local workspace rules when developing this repo |
| `runtime/`, `sdk/`, `tests/`, `scripts/`, `.github/` | Engineering framework — outside plugin component dirs but required product |
| Empty `mcpServers` | Valid MCP config file; no bundled servers required |

## Components intentionally not added

| Component | Reason |
|-----------|--------|
| `.cursor-plugin/marketplace.json` | Single-plugin repository; marketplace manifest is for multi-plugin repos |

## Remaining manual actions

1. Merge PR to `main` when ready.
2. Tag `v2.0.0` (or next patch) after merge.
3. Optional: submit to Cursor Marketplace review at https://cursor.com/marketplace/publish.
4. Enable the local plugin in Cursor after `cle plugin-install` if using `/add-plugin` style loading.

## Validation evidence

- `plugin-validate --self` → PASS (`layout=convention`)
- `verify --path .` → PASS
- `doctor --path .` → PASS
- `pytest` → PASS (68)
- Project install → update → verify → PASS
- Local plugin install → validate (`convention`) → update → PASS
