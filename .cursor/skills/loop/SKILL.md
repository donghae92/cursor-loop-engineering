---
name: loop
description: Advance the failed-section engineering loop
---

# Loop

## When to use

Use after a gate failure to localize, repair, and retest.

## Procedure

1. Read `last_verify.json`.
2. `cle loop --once`.
3. Re-run verify; respect SAFE_STOP / MANUAL_REVIEW.

## Acceptance criteria

- localization recorded
- disposition is IDLE/CONTINUE/SAFE_STOP/MANUAL_REVIEW

## Evidence

loop_state.json + decision_history.jsonl

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
