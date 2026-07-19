---
name: regression-check
description: Run L1–L8 regression gates
---

# Regression Check

## When to use

Use before release or after installer changes.

## Procedure

1. Ensure runtime memory.
2. Trigger regression through `cle verify`.
3. Confirm every level is PASS or FAIL (never silent skip).

## Acceptance criteria

- levels L1–L8 present
- failure_count matches listed failures

## Evidence

regression_history.jsonl

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
