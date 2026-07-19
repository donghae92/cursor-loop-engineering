# Node.js project example

Install Cursor Loop Engineering into a **Node.js** repository (npm, pnpm, or yarn).

## Prerequisites

- Node.js 18+ LTS
- Python 3.10+
- Clone of [cursor-loop-engineering](https://github.com/your-org/cursor-loop-engineering)

## Install

```bash
export CLE_ROOT="$HOME/src/cursor-loop-engineering"
pip install -e "$CLE_ROOT"

cd ~/projects/my-node-app

python3 -m cursor_loop install .
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
python3 -m cursor_loop status
```

## npm scripts integration

Add optional scripts to `package.json`:

```json
{
  "scripts": {
    "cle:verify": "python3 -m cursor_loop verify",
    "cle:status": "python3 -m cursor_loop status",
    "cle:repair": "python3 -m cursor_loop repair"
  }
}
```

Run:

```bash
npm test
npm run cle:verify
```

## Cursor rules for TypeScript

`.cursor/rules/node-api.mdc`:

```yaml
---
description: Express API conventions
globs: "src/**/*.{ts,js,mjs}"
alwaysApply: false
---

# Node API

- Run `npm test` before review.
- Do not commit `.env` files.
```

## Hooks and shell tools

Framework hooks fire on Cursor `Shell` tool use. Prefer npm scripts in agent instructions so commands stay portable across macOS/Linux CI.

## CI

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: "20"
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: npm ci
- run: npm test
- run: pip install -e ./cursor-loop-engineering
- run: python3 -m cursor_loop bootstrap
- run: python3 -m cursor_loop verify
```

## Monorepo (pnpm)

Install at each package or once at root:

```bash
python3 -m cursor_loop install ~/projects/my-monorepo
python3 -m cursor_loop bootstrap --path ~/projects/my-monorepo
```

See [docs/installation.md](../../docs/installation.md#monorepos).
