# Migration guide

Migrations live in `sdk/migrations/` and are registered in `sdk/migrations/registry.json`.

## Apply

```bash
cle update --path /path/to/project
# or explicitly
cle rollback --path /path/to/project   # after a recorded upgrade
```

## Author a migration

1. Create `sdk/migrations/vX_Y_Z__vA_B_C/`
2. Add `upgrade.py` with `upgrade(target, framework_root=None)`
3. Add `rollback.py` with `rollback(target, framework_root=None)`
4. Register both paths in `sdk/migrations/registry.json`

## 2.0.0 notes

Breaking layout changes:

- Canonical assets: `.cursor/` only
- Installer package: `sdk/cursor_loop_install/`
- Migrations: `sdk/migrations/`
