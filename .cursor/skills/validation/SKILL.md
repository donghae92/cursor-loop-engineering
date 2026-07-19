---
name: validation
description: Run and interpret validation gates
---

# Validation

## When to use

Use when checking whether the framework installation is healthy.

## Procedure

1. `cle verify --path .`
2. Inspect failures JSON.
3. `cle doctor --repair` then re-verify.

## Acceptance criteria

- verify result PASS
- failures list empty

## Evidence

`last_verify.json` and doctor report.

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
