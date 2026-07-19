---
name: cle-install
description: Install Cursor Loop Engineering into the current project without manual edits
---

# Install

Install merge-safe Cursor assets into this project:

```bash
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop install .
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop verify --path .
```

To install as a local Cursor plugin for `/add-plugin` style usage:

```bash
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop plugin-install
```
