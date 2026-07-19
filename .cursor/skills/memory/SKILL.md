---
name: memory
description: Inspect and repair durable runtime memory
---

# Memory

## When to use

Use when `.cursor-loop/` is missing or corrupted.

## Procedure

1. `cle bootstrap`
2. Confirm state/loop_state/performance files.
3. Avoid deleting history unless quarantine is required.

## Acceptance criteria

- state.framework set
- loop_state present

## Evidence

state.json hashes and event log

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
