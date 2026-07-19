---
name: research
description: Research repository evidence before mutation
---

# Research

## When to use

Use before non-trivial changes.

## Procedure

1. Search and cite paths.
2. Separate observation vs interpretation.
3. Only then propose minimal change.

## Acceptance criteria

- citations include paths
- no fabricated artifacts

## Evidence

Notes in decision_history or PR body

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
