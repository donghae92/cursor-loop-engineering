# Plugin packaging

This repository follows **current Cursor plugin conventions**.

## Layout

```text
.cursor-plugin/plugin.json
rules/
skills/
agents/
commands/
hooks/hooks.json
hooks/*.py
mcp.json
assets/logo.svg
```

Manifest paths:

- `rules`: `./rules/`
- `skills`: `./skills/`
- `agents`: `./agents/`
- `commands`: `./commands/`
- `hooks`: `./hooks/hooks.json`
- `mcpServers`: `./mcp.json`

`.cursor/` is retained as the **project-install mirror**. The installer copies conventional root components into a consumer project's `.cursor/` tree.

## Commands

```bash
cle plugin-validate --self
cle plugin-doctor --self --repair
cle plugin-install
cle plugin-update
cle plugin-remove
```

See [PLUGIN_COMPATIBILITY_REPORT.md](../PLUGIN_COMPATIBILITY_REPORT.md).
