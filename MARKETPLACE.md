# Cursor Loop Engineering — Marketplace Description

**Cursor Loop Engineering** is a first-class Cursor plugin that installs a complete AI engineering harness into any project.

## What it provides

- **Rules** — Architecture, validation, regression, evidence, loop, safety, and release policies
- **Skills** — Runtime repair, verification, research, release, scheduling, and more
- **Agents** — CEO, Manager, Planner, Researcher, Developer, Reviewer, QA, Regression, Release, Documentation
- **Hooks** — Pre/post task, loop continue, stop, failure, research, and validation lifecycle hooks
- **Slash commands** — `/cle-verify`, `/cle-status`, `/cle-repair`, `/cle-loop`, `/cle-install`, `/cle-update`
- **Installer** — Merge-safe install/update/remove with backups and migrations

## Install

### As a Cursor plugin (local)

```bash
python -m cursor_loop plugin-install
```

Then open Cursor Plugins / Marketplace and enable **Cursor Loop Engineering** from local plugins (`~/.cursor/plugins/local/cursor-loop-engineering`).

### Into a project workspace

```bash
python -m cursor_loop install /path/to/project
python -m cursor_loop verify --path /path/to/project
```

No manual file editing required.

## Compatibility

- Cursor plugin manifest: `.cursor-plugin/plugin.json`
- Python 3.9+
- Works with empty repos, existing projects, and monorepos

## Keywords

cursor-plugin, engineering-loop, rules, skills, agents, hooks, verification, regression, installer
