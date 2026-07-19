# Installer

Install Cursor Loop Engineering into any Cursor project with merge-safe updates.

```bash
# From this repository
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop install /path/to/project
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop verify --path /path/to/project
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop update --path /path/to/project
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop doctor --path /path/to/project --repair
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop remove --path /path/to/project
```

Or:

```bash
python3 install/install.py /path/to/project
```

## Behavior

- Detects existing `.cursor` rules/skills/agents/hooks/commands
- Backs up changed managed files under `.cursor-loop/backups/`
- Merges `hooks.json` without dropping user events
- Preserves unrecognized custom files
- Records install metadata and migration history under `.cursor-loop/`
