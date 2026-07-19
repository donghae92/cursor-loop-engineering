# Upgrade Guide

## Incremental update

```bash
python -m cursor_loop update --path /path/to/project
```

Update:

1. Detects installed version
2. Backs up managed files that would change
3. Merges framework assets without deleting custom files
4. Runs migrations when needed
5. Re-verifies the installation

## Force refresh managed assets

```bash
python -m cursor_loop update --path /path/to/project --force
```

A backup is still written under `.cursor-loop/backups/` before overwrites.

## Check versions

```bash
python -m cursor_loop status --path /path/to/project
```

Reports framework version, installed version, repository version, and pending migrations.
