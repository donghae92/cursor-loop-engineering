# Examples

Per-stack guides for installing Cursor Loop Engineering into different project types. Each example assumes you have cloned the framework repository.

## Framework path

Set once per shell session:

```bash
export CLE_ROOT="$HOME/src/cursor-loop-engineering"   # adjust to your clone
export PATH="$CLE_ROOT/scripts:$PATH"
pip install -e "$CLE_ROOT"
```

## Example READMEs

| Stack | Path | Highlights |
|-------|------|------------|
| Android (Gradle) | [examples/android/README.md](../examples/android/README.md) | AGENTS.md, `.gitignore`, verify in CI |
| Python | [examples/python/README.md](../examples/python/README.md) | venv, pytest + verify |
| Node.js | [examples/node/README.md](../examples/node/README.md) | npm project, hook paths |
| Flutter | [examples/flutter/README.md](../examples/flutter/README.md) | Dart project layout |
| Rust | [examples/rust/README.md](../examples/rust/README.md) | Cargo workspace |

## Common install sequence

Every stack follows the same core commands:

```bash
python3 -m cursor_loop install /path/to/project
cd /path/to/project
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
python3 -m cursor_loop status
```

## In-repo example

See `.cursor/examples/verify-flow.md` for the canonical verify flow copied on install.

## Customizing after install

1. Add project rules: `.cursor/rules/my-project.mdc`
2. Add project skills: `.cursor/skills/my-skill/SKILL.md`
3. Extend `AGENTS.md` with stack-specific commands
4. Commit `.cursor/` to pin framework version; ignore volatile `.cursor-loop/` paths as needed

## CI snippet

```yaml
- run: pip install -e "$CLE_ROOT"
- run: python3 -m cursor_loop bootstrap --path "${{ github.workspace }}"
- run: python3 -m cursor_loop verify --path "${{ github.workspace }}"
```

## Related

- [Installation](installation.md)
- [Quick start](quick-start.md)
- [Migration guide](migration-guide.md)
