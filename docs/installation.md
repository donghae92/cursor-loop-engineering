# Installation Guide

## Install into an existing project

```bash
git clone https://github.com/donghae92/cursor-loop-engineering.git
cd cursor-loop-engineering
pip install -e ".[dev]"

python -m cursor_loop install /path/to/your/project
python -m cursor_loop verify --path /path/to/your/project
```

## Install into an empty repository

```bash
mkdir my-app && cd my-app
python -m cursor_loop install .
python -m cursor_loop bootstrap --path .
python -m cursor_loop verify --path .
```

## Install from a GitHub Release

```bash
python -m cursor_loop import cursor-loop-engineering-1.1.0.tar.gz --target /path/to/project
python -m cursor_loop verify --path /path/to/project
```

## What gets installed

- `.cursor/rules`, `skills`, `agents`, `hooks`, `templates`, `examples`
- `.cursor/hooks.json` (merged if already present)
- `.cursor-loop/` runtime memory and install manifest

Custom files you already have under `.cursor/` are preserved.
