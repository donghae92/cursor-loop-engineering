---
name: scheduler
description: Synchronize dependency-aware task queues
---

# Scheduler

## When to use

Use when planning or refreshing engineering tasks.

## Procedure

1. Ensure templates under `.cursor/templates/`.
2. Run scheduler via verify/bootstrap path or status.
3. Inspect ready/done task ids.

## Acceptance criteria

- task_queue.jsonl updated
- dependencies respected

## Evidence

task_queue.jsonl summary in status output

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
