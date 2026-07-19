---
name: release
description: Package and gate a release
---

# Release

## When to use

Use when cutting a versioned release.

## Procedure

1. `cle verify` PASS
2. `cle release` or `cle export`
3. Confirm archive + sha256

## Acceptance criteria

- archive exists
- VERSION matches package metadata

## Evidence

dist/*.tar.gz and *.sha256

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
