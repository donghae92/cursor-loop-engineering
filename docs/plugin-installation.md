# Plugin installation

## Local `/add-plugin` style install

```bash
cle plugin-validate --self
cle plugin-install
# optional custom directory
cle plugin-install --target /path/to/plugins/local
```

Destination:

`~/.cursor/plugins/local/cursor-loop-engineering`

Then enable the plugin in Cursor.

## Project install (recommended for repos)

```bash
cle install /path/to/project
cle verify --path /path/to/project
```

This writes assets into the project's `.cursor/` tree with merge-safe backups.
