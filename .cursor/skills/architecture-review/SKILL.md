---
name: architecture-review
description: Review layer boundary violations
---

# Architecture Review

## When to use

Use during PR review of framework changes.

## Procedure

1. Ensure assets remain under `.cursor/`.
2. Ensure Python remains under runtime/sdk.
3. Reject dual sources of truth.

## Acceptance criteria

- no root rules/skills/agents mirrors required for source
- docs match layout

## Evidence

tree listing + docs diff

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
