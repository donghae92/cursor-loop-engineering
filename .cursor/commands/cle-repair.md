---
name: cle-repair
description: Diagnose and repair a Cursor Loop Engineering installation
---

# Repair

```bash
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop doctor --path . --repair
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop repair --path .
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop verify --path .
```

Preserve custom `.cursor` files. Backups live under `.cursor-loop/backups/`.
