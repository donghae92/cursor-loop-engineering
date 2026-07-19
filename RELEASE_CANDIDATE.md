# RELEASE CANDIDATE REPORT

**Product:** Cursor Loop Engineering  
**Version:** 2.0.0  
**Branch:** `cursor/production-v2`  
**Date:** 2026-07-20  
**Disposition:** RELEASE CANDIDATE — ready for tag after merge to `main`

---

## Architecture

Frozen production layout (no redesign):

| Path | Role |
|------|------|
| `.cursor/` | Canonical Cursor assets (rules, skills, agents, hooks, commands, templates) |
| `.cursor-plugin/plugin.json` | Plugin manifest (custom paths into `.cursor/`) |
| `assets/` | Marketplace logo |
| `runtime/cursor_loop_runtime/` | Loop, scheduler, regression L1–L8, evidence, memory, checkpoint |
| `sdk/cursor_loop/` | CLI |
| `sdk/cursor_loop_install/` | Installer, doctor, verify, plugin lifecycle, export/import |
| `sdk/migrations/` | Version upgrades / rollbacks |
| `docs/` | Documentation |
| `examples/` | Stack install guides |
| `tests/` | Automated tests |
| `scripts/` | `cle`, sync, install entry |
| `.github/` | CI + release workflows |

**Plugin loading model**

1. Source repository keeps assets under `.cursor/` (workspace + framework source of truth).
2. `cle plugin-install` materializes marketplace-conventional root dirs (`rules/`, `skills/`, …) under `~/.cursor/plugins/local/cursor-loop-engineering`.
3. Project install copies `.cursor/` into consumer projects with merge-safe backups.

This matches Cursor plugin conventions for installed plugins while preserving the frozen source architecture.

---

## Version

| Artifact | Value |
|----------|-------|
| `VERSION` | `2.0.0` |
| `pyproject.toml` | `2.0.0` |
| `.cursor-plugin/plugin.json` | `2.0.0` |
| `COMPATIBILITY.json` | `2.0.0` |
| Package `__init__` modules | `2.0.0` |

---

## Compatibility

- **Python:** 3.9+ (recommended 3.11; CI: 3.9 / 3.11 / 3.12 on Linux/macOS/Windows)
- **Cursor:** Plugins + hooks support required for full local plugin loading
- **Migrations:** `1.0.0 → 1.1.0 → 1.2.0 → 2.0.0`
- **MCP:** `mcp.json` present with empty `mcpServers` (extend per deployment)

---

## Inventory

| Component | Count |
|-----------|------:|
| Rules | 12 |
| Skills | 14 |
| Agents | 10 |
| Commands | 6 |
| Hook scripts | 8 (incl. `_common.py`) |
| Hook events configured | preToolUse, postToolUse, onError, stop, sessionStart |

---

## Verification status

| Gate | Result |
|------|--------|
| `python3 -m cursor_loop plugin-validate --self` | PASS |
| `python3 -m cursor_loop verify --path .` | PASS |
| `python3 -m cursor_loop doctor --path .` | PASS |
| `pytest` | PASS (68) |
| Project install → verify | PASS |
| Project update path | PASS |
| Local plugin install / validate / update / remove | PASS |
| Materialized plugin layout validation | PASS |
| Release workflow export JSON parse | FIXED |
| Teleport / AddressCatcher residue | NONE |

---

## Marketplace readiness

| Item | Status |
|------|--------|
| `.cursor-plugin/plugin.json` required `name` | PASS |
| Version / description / author / license | PASS |
| Logo `assets/logo.svg` | PASS |
| Component paths resolve | PASS |
| `mcp.json` present | PASS |
| `MARKETPLACE.md` | PASS |
| SECURITY / LICENSE / CHANGELOG / CONTRIBUTING | PASS |
| Issue templates + PR template | PASS |
| Single-plugin repo (no marketplace.json needed) | PASS |

Official Cursor docs prefer root `rules/`/`skills/` folders for plugin packages. This repository intentionally keeps `.cursor/` as source and materializes root folders at local plugin install time.

---

## Known limitations

1. **Empty MCP servers** — no bundled third-party MCP servers; consumers add their own.
2. **Examples are documentation guides** — not full fixture applications.
3. **Marketplace listing** — still requires Cursor team review at https://cursor.com/marketplace/publish.
4. **Source vs installed layout** — git source uses `.cursor/` paths in the manifest; installed local plugin uses materialized root component dirs.
5. **Hook coverage tests** — functional hooks exist; dedicated stdin/stdout contract tests are limited.

---

## Outstanding risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Cursor marketplace review may require root-only component dirs in the published git tree | Medium | Local install already materializes convention layout; if required, publish from a packaging step without redesigning source |
| Multi-OS CI matrix flakiness | Low | Existing matrix; investigate per-OS failures if they appear |
| Consumers on 1.x skipping migrations | Medium | Documented upgrade path; `cle update` applies registry steps |

---

## Blocking issues

**Zero blocking issues remaining** after RC polish on this branch.

---

## Release checklist

- [x] Architecture frozen
- [x] Plugin manifest validated
- [x] Install / update / local plugin load validated
- [x] Docs: README, CHANGELOG, LICENSE, SECURITY, CONTRIBUTING, issue/PR templates, RELEASE_NOTES
- [x] CI/release workflows repaired
- [ ] Merge `cursor/production-v2` → `main`
- [ ] Tag `v2.0.0`
- [ ] Confirm GitHub Release assets
- [ ] Submit marketplace review if desired

---

## Sign-off

Release Candidate quality achieved for **Cursor Loop Engineering 2.0.0**.  
Architecture remains frozen; only production-quality repairs were applied.
