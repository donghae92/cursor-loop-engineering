# Quick start

Get Cursor Loop Engineering running on a project in about five minutes.

## 1. Clone and install the framework

```bash
git clone https://github.com/your-org/cursor-loop-engineering.git
cd cursor-loop-engineering
pip install -e .
```

Verify the CLI:

```bash
python3 -m cursor_loop doctor --self 2>/dev/null || python3 -m cursor_loop doctor
cle --help 2>/dev/null || python3 -m cursor_loop --help
```

Without pip install, use the launcher script:

```bash
./scripts/cle doctor
```

## 2. Bootstrap the framework repository

When working inside the framework repo itself:

```bash
python3 -m cursor_loop bootstrap --self
python3 -m cursor_loop verify
python3 -m cursor_loop status
```

Expected: `verify` returns `"result": "PASS"` and creates `.cursor-loop/` with state files.

## 3. Install into your project

Point `install` at any existing repository (Android, Node, Python, etc.):

```bash
python3 -m cursor_loop install /path/to/your-project
cd /path/to/your-project
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
```

This copies:

- `.cursor/rules/`, `skills/`, `agents/`, `hooks/`
- `.cursor/hooks.json`
- `.cursor/templates/` and `examples/`

It also creates `.cursor-loop/install_manifest.json` with file hashes and may add a starter `AGENTS.md`.

## 4. Open in Cursor

1. Open the target project in Cursor.
2. Confirm rules appear under **Cursor Settings → Rules**.
3. Invoke skills by name when prompting (e.g., "use the validation skill").
4. Subagents can be launched per `.cursor/agents/*.md` definitions.

## 5. Daily commands

```bash
# Check health
python3 -m cursor_loop status

# Run all gates
python3 -m cursor_loop verify

# After a failed gate, advance the repair loop once
python3 -m cursor_loop loop --once

# Inspect loop disposition without advancing
python3 -m cursor_loop loop --status

# Fix permissions and re-verify
python3 -m cursor_loop repair

# Release checkpoint (requires verify PASS)
python3 -m cursor_loop release
```

## 6. Typical verify flow

From `.cursor/examples/verify-flow.md`:

```bash
python3 -m cursor_loop install .
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
python3 -m cursor_loop status
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Command succeeded |
| 3 | Loop stopped (`SAFE_STOP` or `MANUAL_REVIEW`) |
| 4 | Verification or repair failed |
| 5 | Unexpected error |

Parse JSON stdout in scripts:

```bash
python3 -m cursor_loop verify | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d['result']=='PASS' else 1)"
```

## Next steps

- [Installation](installation.md) — CI, upgrades, monorepos
- [Architecture](architecture.md) — Controllers and memory layout
- [Loop engineering guide](loop-engineering-guide.md) — Repair loops and dispositions
- [Examples](examples.md) — Stack-specific install READMEs

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `.cursor-loop missing` | `python3 -m cursor_loop bootstrap` |
| `hook not executable` | `python3 -m cursor_loop repair` |
| `verify` FAIL on rules/skills | `python3 -m cursor_loop update` to refresh assets |
| Python too old | Use Python 3.10+ (`doctor` reports version) |

Run diagnostics:

```bash
python3 -m cursor_loop doctor
```
