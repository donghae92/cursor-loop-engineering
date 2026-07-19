# AGENTS.md

This repository is **Cursor Loop Engineering** — a generic Cursor engineering framework.

## Authority

1. `.cursor/rules/`
2. `.cursor/skills/`
3. Runtime controllers in `runtime/cursor_loop_runtime/`
4. CLI: `cle` / `python3 -m cursor_loop`

## Quick commands

```bash
cle status
cle verify
cle loop --once
cle doctor --repair
```

## Boundaries

- Cursor assets: `.cursor/` only
- Runtime memory: `.cursor-loop/` only
- Python packages: `runtime/` and `sdk/`
- No project-specific or proprietary product logic in this framework
