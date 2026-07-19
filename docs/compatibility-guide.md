# Compatibility Guide

See [`COMPATIBILITY.json`](../COMPATIBILITY.json) for the machine-readable matrix.

## Current

- Framework version: **1.1.0**
- Minimum Python: **3.9**
- Hooks schema version: **1**

## Upgrade path

`1.0.0` → `1.1.0` via `migration/v1_0_0__v1_1_0`

## Supported project shapes

- Empty repositories
- Existing Cursor projects
- Monorepos (`packages/`, `apps/`, multi-ecosystem markers)
- Small and large repositories

Compatibility is based on the Cursor asset contract (rules/skills/agents/hooks) and runtime layout under `.cursor-loop/`, not on application business logic.
