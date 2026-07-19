# Installation

## Into any project

```bash
pip install -e /path/to/cursor-loop-engineering
cle install /path/to/your-project
cle verify --path /path/to/your-project
```

The installer:

1. Detects empty / existing / monorepo layouts
2. Copies canonical assets from the framework `.cursor/` tree
3. Merges `hooks.json` without discarding custom entries
4. Writes backups under `.cursor-loop/backups/` before overwrites
5. Records `install_manifest.json` with file hashes

No manual `.cursor/` edits are required for a standard install.

## Self bootstrap (this repository)

```bash
cle bootstrap --self
cle verify
```

## Update / repair / remove

```bash
cle update --path /path/to/project
cle doctor --path /path/to/project --repair
cle remove --path /path/to/project
```
