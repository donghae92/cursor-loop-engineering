# Migration guide

Upgrade Cursor Loop Engineering in target projects without losing project-specific Cursor assets.

## Versioning

- Framework version is declared in `pyproject.toml` and `install_manifest.json` (`version: 1.0.0`).
- Installed file hashes are recorded in `.cursor-loop/install_manifest.json`.

Check current install:

```bash
python3 -c "import json; print(json.load(open('.cursor-loop/install_manifest.json'))['version'])"
```

## Upgrade framework checkout

```bash
cd /path/to/cursor-loop-engineering
git pull
pip install -e .
```

## Refresh assets in a target project

```bash
python3 -m cursor_loop update --path /path/to/project
# equivalent to: install --force
python3 -m cursor_loop bootstrap --path /path/to/project
python3 -m cursor_loop verify --path /path/to/project
```

`update` overwrites framework-managed files under `.cursor/` (rules, skills, agents, hooks, templates, examples, hooks.json). It does **not** delete custom files you added unless names collide.

## Preserve project customizations

| Asset | Merge strategy |
|-------|----------------|
| Custom rules `my-*.mdc` | Safe — verify only checks bundled rule names |
| Custom skills/agents | Safe if unique directory names |
| Edited bundled `architecture.mdc` | **Overwritten** on update — fork or re-apply edits |
| `AGENTS.md` | Not overwritten if present |
| `.cursor-loop/` | Preserved; bootstrap fills missing files only |

**Recommendation:** Keep project-specific rules in separately named files (e.g., `acme-api.mdc`) rather than editing bundled policy files.

## Hash and regression changes

Updating bundled rules or hooks changes L2 regression hashes. After update:

1. Run verify and confirm PASS.
2. If FAIL on regress, inspect `regression_history.jsonl`.
3. Record baseline change in project CHANGELOG.

Use the `hash-audit` skill to compare manifest before/after:

```bash
cp .cursor-loop/install_manifest.json /tmp/manifest.before.json
python3 -m cursor_loop update
diff /tmp/manifest.before.json .cursor-loop/install_manifest.json
```

## Migrating from ad-hoc Cursor setup

If the project already has `.cursor/rules` without the framework:

```bash
# Backup
tar -czf cursor-backup.tgz .cursor

python3 -m cursor_loop install .
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
```

Resolve duplicate rule names manually; merge content from backup into project-specific files.

## Migrating runtime memory

`.cursor-loop/` is version-agnostic JSON. New fields are added by `MemoryController.ensure()` without deleting existing history.

To reset loop state only:

```bash
rm -f .cursor-loop/loop_state.json
python3 -m cursor_loop bootstrap
```

To full reset (destructive):

```bash
rm -rf .cursor-loop
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
```

## Downgrade

Install an older framework tag, then:

```bash
git checkout v1.0.0
pip install -e .
python3 -m cursor_loop update --path /path/to/project
python3 -m cursor_loop verify --path /path/to/project
```

Verify PASS is required before release on any version.

## CI migration

Add verify to existing pipelines:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install -e ./cursor-loop-engineering
- run: python3 -m cursor_loop verify
```

## Breaking change policy

Semver for the framework:

- **Major** — CLI contract, hooks.json schema, required verify assets
- **Minor** — New skills, agents, optional controllers
- **Patch** — Docs, hook message text, non-breaking fixes

See [CHANGELOG.md](../CHANGELOG.md) for release notes.

## Related

- [Installation](installation.md)
- [Architecture](architecture.md)
- [Contributing](../CONTRIBUTING.md)
