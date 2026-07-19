# Troubleshooting

## `verify` fails with missing assets

```bash
python -m cursor_loop doctor --path . --repair
python -m cursor_loop verify --path .
```

## Hooks were overwritten

Installer merges `hooks.json`. If a managed file was force-updated, restore from:

`.cursor-loop/backups/<timestamp>-*/`

```bash
# inspect backups then copy files back manually, or re-run update after restoring
```

## Hash drift warnings

Custom edits to managed files produce hash drift in doctor output. Either:

- keep the customization and ignore drift, or
- run `python -m cursor_loop update --force` to refresh managed content (backup first)

## Remove the framework

```bash
python -m cursor_loop remove --path .
python -m cursor_loop remove --path . --purge-runtime
```

## Import/export issues

```bash
python -m cursor_loop export --output dist
python -m cursor_loop import dist/cursor-loop-engineering-1.1.0.tar.gz --target /path/to/project
```

Ensure the archive checksum file matches before importing in production pipelines.
