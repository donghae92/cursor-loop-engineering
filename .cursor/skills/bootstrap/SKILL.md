---
name: bootstrap
description: Bootstrap Cursor Loop runtime memory and assets
---

# Bootstrap

## When to use

Use when initializing a project with Cursor Loop Engineering.

## Procedure

1. Run `cle bootstrap` or `cle install <path>`.
2. Confirm `.cursor/` and `.cursor-loop/` exist.
3. Run `cle verify`.

## Acceptance criteria

- `.cursor/hooks.json` exists
- `.cursor-loop/state.json` exists
- verify returns PASS

## Evidence

Install manifest + verify JSON under `.cursor-loop/`.

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
