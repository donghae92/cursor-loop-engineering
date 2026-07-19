# Plugin packaging

Source of truth for Cursor assets is `.cursor/`.

`.cursor-plugin/plugin.json` points at:

- `./.cursor/rules/`
- `./.cursor/skills/`
- `./.cursor/agents/`
- `./.cursor/commands/`
- `./.cursor/hooks.json`
- `./mcp.json`

Local plugin install materializes a Cursor-compatible root layout under `~/.cursor/plugins/local/cursor-loop-engineering` (rules/skills/agents at plugin root) without keeping those mirrors in git.

```bash
cle plugin-validate --self
cle plugin-doctor --self --repair
cle plugin-install
cle plugin-update
cle plugin-remove
```
