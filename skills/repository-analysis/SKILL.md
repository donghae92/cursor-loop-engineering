---
name: repository-analysis
description: Analyze project shape for install strategy
---

# Repository Analysis

## When to use

Use before installing into an unfamiliar repo.

## Procedure

1. Detect empty/existing/monorepo.
2. Choose merge-safe install.
3. Backup before overwrite.

## Acceptance criteria

- detection recorded
- backup created when overwriting

## Evidence

install report + backups/

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
