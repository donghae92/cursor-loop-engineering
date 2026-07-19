---
name: graph-builder
description: Build task dependency awareness
---

# Graph Builder

## When to use

Use when extending the default task graph.

## Procedure

1. Edit `.cursor/templates/task.json` tasks list or rely on defaults.
2. Run scheduler.
3. Verify dependency order.

## Acceptance criteria

- waiting tasks blocked by unmet deps
- ready tasks have deps DONE

## Evidence

task_queue.jsonl

## Stop conditions

- Identical failure without progress → SAFE_STOP
- Missing authority or ambiguous ownership → MANUAL_REVIEW
- Gate PASS with durable artifacts recorded under `.cursor-loop/`
