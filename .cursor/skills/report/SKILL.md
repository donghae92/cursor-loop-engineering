---
name: report
description: Produce structured status reports
---

# Report

## When to use

Use when summarizing framework health for humans.

## Procedure

1. `cle status`
2. Include version, detection, loop disposition, last verify.
3. Do not claim PASS without JSON evidence.

## Acceptance criteria

- report references concrete artifacts

## Evidence

status JSON

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
