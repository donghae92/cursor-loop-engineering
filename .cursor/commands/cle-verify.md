---
name: cle-verify
description: Run Cursor Loop Engineering verification on the current project
---

# Verify

Run the framework verifier and report PASS/FAIL with concrete failures.

```bash
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop verify --path .
```

If the CLI is installed:

```bash
cle verify --path .
```

On FAIL, run `/cle-repair` or `cle doctor --repair`.
