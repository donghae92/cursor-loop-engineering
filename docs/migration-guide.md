# Migration Guide

Migrations live in `migration/` and are registered in `migration/registry.json`.

## Apply upgrades

```bash
python -m cursor_loop update --path /path/to/project
```

Or install a newer package; migrations run automatically when the installed version differs.

## Roll back

```bash
python -m cursor_loop rollback --path /path/to/project
python -m cursor_loop rollback --path /path/to/project --migration-id v1_0_0__v1_1_0
```

## History

Migration events are appended to:

`.cursor-loop/migration_history.jsonl`

## Authoring a migration

1. Create `migration/vX_Y_Z__vA_B_C/`
2. Add `upgrade.py` with `upgrade(target, framework_root=None)`
3. Add `rollback.py` with `rollback(target, framework_root=None)`
4. Register both paths in `migration/registry.json`
5. Bump `VERSION` and update `COMPATIBILITY.json`
