# Installation

This guide covers installing Cursor Loop Engineering as a Python package and deploying it into target projects.

## Requirements

- **Python** 3.10 or newer (3.11 used in CI)
- **Git** for cloning the framework repository
- **Cursor** IDE for rules, skills, agents, and hooks to take effect

No runtime Python dependencies are required for the core package.

## Install the framework package

### Editable install (development)

```bash
git clone https://github.com/your-org/cursor-loop-engineering.git
cd cursor-loop-engineering
pip install -e .
```

This registers the `cle` console script pointing to `cursor_loop.cli:main`.

### Run without installing

From the framework repository root:

```bash
export PYTHONPATH="$(pwd)/sdk:$(pwd)/runtime${PYTHONPATH:+:$PYTHONPATH}"
python3 -m cursor_loop doctor
# or
./scripts/cle doctor
```

### Verify package layout

```bash
python3 -c "from cursor_loop.paths import framework_root; print(framework_root())"
python3 -c "import cursor_loop_runtime; print(cursor_loop_runtime.__file__)"
```

Both packages resolve from `sdk/` and `runtime/` via `pyproject.toml`:

```toml
[tool.setuptools.packages.find]
where = ["sdk", "runtime"]
```

## Install into a target project

The `install` command copies framework Cursor assets; it does **not** modify application source except optionally creating `AGENTS.md`.

```bash
python3 -m cursor_loop install /path/to/project
```

Options:

- **Default target** — Current directory if omitted: `cle install .`
- **`--force`** — Overwrite framework-managed files on update

Post-install steps **in the target project**:

```bash
cd /path/to/project
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
```

### What gets copied

| Source (framework repo) | Destination (target) |
|-------------------------|----------------------|
| `.cursor/hooks.json` | `.cursor/hooks.json` |
| `.cursor/rules/` | `.cursor/rules/` |
| `.cursor/skills/` | `.cursor/skills/` |
| `.cursor/agents/` | `.cursor/agents/` |
| `.cursor/hooks/` | `.cursor/hooks/` |
| `.cursor/templates/` | `.cursor/templates/` |
| `.cursor/examples/` | `.cursor/examples/` |

Hook scripts are marked executable automatically.

### Install manifest

After install, inspect:

```bash
cat .cursor-loop/install_manifest.json
```

Contains framework version, timestamps, source path, and SHA-256 per installed file.

## Bootstrap runtime memory

`bootstrap` creates `.cursor-loop/` and initial JSON/JSONL files:

```bash
python3 -m cursor_loop bootstrap          # current project
python3 -m cursor_loop bootstrap --path /path/to/project
python3 -m cursor_loop bootstrap --self   # framework repo only
```

Bootstrap also runs the scheduler once and creates a bootstrap checkpoint.

## Update framework assets

To refresh Cursor assets from a newer framework checkout:

```bash
# From framework repo with target path
python3 -m cursor_loop update --path /path/to/project
```

Implementation: reinstall with `--force`.

## Git ignore recommendations

Add to the target project's `.gitignore`:

```gitignore
# Cursor Loop runtime memory (optional — some teams commit state.json)
.cursor-loop/quarantine/
.cursor-loop/runtime/
.cursor-loop/checkpoints/
```

Teams often **commit** `.cursor/` after install to pin framework versions, and **ignore** volatile runtime files under `.cursor-loop/`.

## CI integration

Example GitHub Actions step (see `.github/workflows/ci.yml` in this repo):

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install -e .
- run: python3 -m cursor_loop bootstrap
- run: python3 -m cursor_loop verify
```

Fail the job on non-zero exit or `"result": "FAIL"` in JSON.

## Monorepos

Install into each package root that uses Cursor independently:

```bash
for dir in apps/web apps/api services/worker; do
  python3 -m cursor_loop install "$dir"
  python3 -m cursor_loop bootstrap --path "$dir"
done
```

Alternatively install once at the monorepo root if all agents share one Cursor workspace.

## Docker / remote dev

Mount the framework repo and set `PYTHONPATH`:

```dockerfile
ENV PYTHONPATH=/opt/cursor-loop-engineering/sdk:/opt/cursor-loop-engineering/runtime
RUN python3 -m cursor_loop install /app && python3 -m cursor_loop bootstrap --path /app
```

## Uninstall

Remove copied assets and runtime memory:

```bash
rm -rf .cursor/rules .cursor/skills .cursor/agents .cursor/hooks .cursor/templates .cursor/examples
rm -f .cursor/hooks.json
rm -rf .cursor-loop
```

Restore from git if `.cursor/` was committed before install.

## Related

- [Quick start](quick-start.md)
- [Migration guide](migration-guide.md)
- [Examples](examples.md)
