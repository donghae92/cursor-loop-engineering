# RELEASE CANDIDATE

**Product:** Cursor Loop Engineering  
**Version recommendation:** `2.0.0` (ship this tag; first production release of the stabilized plugin/framework)  
**Branch:** `cursor/production-v2`  
**Date:** 2026-07-20  
**Disposition:** RELEASE CANDIDATE — ready for GitHub merge/release

---

## Repository status

Internally consistent and release-ready.

| Area | Status |
|------|--------|
| Plugin convention layout | PASS — root `rules/`, `skills/`, `agents/`, `commands/`, `hooks/` |
| `.cursor-plugin/plugin.json` | PASS — conventional paths |
| `mcp.json` | PASS — present |
| Documentation set | PASS — README, CHANGELOG, LICENSE, CONTRIBUTING, SECURITY, RELEASE_NOTES |
| Examples | PASS — stack install guides under `examples/` |
| Tests | PASS |
| Proprietary / project-specific residue | NONE |
| Obsolete generators / dual-source scripts | NONE |

Architecture is frozen. This pass did not redesign or expand scope.

---

## Plugin compatibility

Aligned with current Cursor plugin conventions:

```text
.cursor-plugin/plugin.json
rules/
skills/
agents/
commands/
hooks/hooks.json
hooks/*.py
mcp.json
assets/logo.svg
README.md
```

| Manifest field | Value |
|----------------|-------|
| `name` | `cursor-loop-engineering` |
| `version` | `2.0.0` |
| `rules` | `./rules/` |
| `skills` | `./skills/` |
| `agents` | `./agents/` |
| `commands` | `./commands/` |
| `hooks` | `./hooks/hooks.json` |
| `mcpServers` | `./mcp.json` |
| `logo` | `assets/logo.svg` |

`.cursor/` is retained only as the **project-install mirror** (consumer projects receive assets under `.cursor/`). That is intentional and required for the installer.

Single-plugin repository: no `.cursor-plugin/marketplace.json` (not required).

See also `PLUGIN_COMPATIBILITY_REPORT.md`.

---

## Verification results

| Gate | Result |
|------|--------|
| `python3 -m cursor_loop plugin-validate --self` | PASS (`layout=convention`) |
| `python3 -m cursor_loop verify --path .` | PASS |
| `python3 -m cursor_loop doctor --path .` | PASS |
| `pytest` | PASS (68) |
| Project install → update → verify | PASS (prior stabilization) |
| Local plugin install → validate → update | PASS (prior stabilization) |

**Blocking issues remaining:** 0

---

## Known limitations

1. `mcp.json` ships with empty `mcpServers` — consumers add servers as needed.
2. `examples/` are documentation guides, not full application fixtures.
3. Marketplace listing still requires Cursor team review if publishing publicly.
4. Semver is `2.0.0` because of the prior 1.x → 2.0 migration lineage; this is the first production ship of the stabilized plugin layout (not a new post-RC redesign).

---

## Release checklist

- [x] Cursor plugin convention layout verified
- [x] Plugin manifest validated
- [x] README / CHANGELOG / LICENSE / CONTRIBUTING / SECURITY / RELEASE_NOTES present
- [x] Tests and `cle verify` PASS
- [x] No proprietary project residue
- [x] Tag `v2.0.0` prepared on branch history
- [ ] Merge `cursor/production-v2` → `main` (manual)
- [ ] Confirm GitHub Release assets after merge (manual)
- [ ] Optional: submit marketplace review (manual)

---

## Version recommendation

**Ship `v2.0.0`.**

Do not start a new major redesign. Do not invent v3 systems. Treat this RC as the finished production baseline for the current product line.

---

## Sign-off

Release Candidate quality achieved. Stop further improvement work until after GitHub merge/release.
