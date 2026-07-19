---
name: hash-audit
description: Audit managed file hashes
---

# Hash Audit

## When to use

Use when L2 hash failures occur.

## Procedure

1. Read install_manifest.json.
2. Recompute sha256 for listed paths.
3. Update only via installer after backup.

## Acceptance criteria

- mismatches listed precisely

## Evidence

manifest + sha256 digests

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
