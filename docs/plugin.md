# Plugin Documentation

Cursor Loop Engineering is packaged as a Cursor plugin.

## Manifest

[`.cursor-plugin/plugin.json`](../.cursor-plugin/plugin.json)

## Component layout

| Path | Purpose |
|------|---------|
| `rules/` | Policy rules (`.mdc`) |
| `skills/` | Agent skills |
| `agents/` | Subagent definitions |
| `commands/` | Slash commands |
| `hooks/` | Hook scripts + `hooks.json` |
| `mcp.json` | MCP server configuration (empty by default) |
| `templates/` | Runtime templates |
| `examples/` | Usage examples |
| `assets/` | Logo and media |

Workspace mirror under `.cursor/` is kept for opening this repository as a Cursor project. Run:

```bash
python scripts/sync_plugin_layout.py
```

## Commands

```bash
python -m cursor_loop plugin-validate --self
python -m cursor_loop plugin-doctor --self --repair
python -m cursor_loop plugin-install
python -m cursor_loop plugin-update
python -m cursor_loop plugin-remove
```

## Local plugin path

Installs to:

`~/.cursor/plugins/local/cursor-loop-engineering`

This is the path Cursor uses for local `/add-plugin` style discovery.
