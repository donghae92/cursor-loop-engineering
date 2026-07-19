---
name: cle-update
description: Update Cursor Loop Engineering assets while preserving customizations
---

# Update

```bash
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop update --path .
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop plugin-update
```

Managed files are backed up before overwrite. Custom rules/skills/commands are preserved.
