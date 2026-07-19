# Changelog

All notable changes to Cursor Loop Engineering are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-19

### Added

- **CLI** — `install`, `bootstrap`, `verify`, `doctor`, `loop`, `status`, `update`, `repair`, and `release` commands via `python3 -m cursor_loop`, `scripts/cle`, or `cle` after pip install.
- **Runtime controllers** — Memory, loop, scheduler, task queue, state machine, regression, evidence, and checkpoint managers under `runtime/cursor_loop_runtime/`.
- **Cursor assets** — Twelve policy rules, fourteen skills, ten agent roles, and seven lifecycle hooks with `hooks.json` v1 schema.
- **Install pipeline** — Copies `.cursor/` assets into target projects, writes `install_manifest.json` with SHA-256 hashes, and seeds `AGENTS.md` when missing.
- **Runtime memory** — Durable JSON/JSONL state under `.cursor-loop/` including loop disposition, performance timings, decision history, and checkpoints.
- **Regression framework** — L1 schema and L2 hash integrity checks with versioned baselines.
- **Loop policy** — Failed-section repair with retry budget, identical-failure detection, and `SAFE_STOP` / `MANUAL_REVIEW` dispositions.
- **Documentation** — Full docs tree, GitHub templates, CI workflow, and per-stack example READMEs.

### Requirements

- Python 3.10 or newer (3.11 recommended for CI).

[1.0.0]: https://github.com/your-org/cursor-loop-engineering/releases/tag/v1.0.0
