# Python project example

Install Cursor Loop Engineering into a **Python application or library** (venv, Poetry, or plain `pyproject.toml`).

## Prerequisites

- Python 3.10+
- Clone of [cursor-loop-engineering](https://github.com/your-org/cursor-loop-engineering)

## Install

```bash
export CLE_ROOT="$HOME/src/cursor-loop-engineering"
pip install -e "$CLE_ROOT"

cd ~/projects/my-python-app

python3 -m cursor_loop install .
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
```

## Virtual environment workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "$CLE_ROOT"
pip install -e ".[dev]"   # your project

python3 -m cursor_loop doctor
python3 -m cursor_loop status
```

## Customize rules

Create `.cursor/rules/python-app.mdc`:

```yaml
---
description: Python app testing and typing standards
globs: "**/*.py"
alwaysApply: false
---

# Python standards

- Run `pytest` before review.
- Use type hints on public APIs.
```

Framework `coding-standards.mdc` already applies to framework paths; your rule covers application code.

## Daily loop

```bash
pytest
python3 -m cursor_loop verify
python3 -m cursor_loop loop --status
```

On verify FAIL:

```bash
python3 -m cursor_loop repair
python3 -m cursor_loop loop --once
```

## CI

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install -e ./cursor-loop-engineering
- run: pip install -e ".[dev]"
- run: pytest
- run: python3 -m cursor_loop bootstrap
- run: python3 -m cursor_loop verify
```

## Release

```bash
python3 -m cursor_loop verify
python3 -m cursor_loop release
```

See [docs/quick-start.md](../../docs/quick-start.md).
