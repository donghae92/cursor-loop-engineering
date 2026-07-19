---
name: runtime-repair
description: Diagnose and repair degraded runtime
---

# Runtime Repair

## When to use

Use when doctor reports missing assets or DEGRADED health.

## Procedure

1. `cle doctor --repair`
2. `cle repair`
3. `cle verify`

## Acceptance criteria

- doctor issues empty or repaired
- health HEALTHY

## Evidence

doctor JSON + verify JSON

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
