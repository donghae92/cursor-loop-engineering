# Changelog

## [2.0.0] - 2026-07-19

### Added

- Production layout with `.cursor/` as the sole Cursor asset source of truth.
- Full regression levels L1–L8 (schema, hash, provenance, semantic, temporal, dependency, representative, boot).
- Loop localize → deterministic repair → retest behavior.
- Dependency-aware scheduler with template-driven task specs.
- Evidence class allow-list and artifact existence checks.
- Hook safety denials for destructive shell patterns and secret-like material.
- Migration `1.2.0` → `2.0.0`.

### Changed

- Installer moved to `sdk/cursor_loop_install/`; migrations to `sdk/migrations/`.
- Plugin local install materializes root component dirs from `.cursor/` at install time only.
- Removed committed root mirrors (`rules/`, `skills/`, `agents/`, `hooks/`, `commands/`, `templates/`).
- Removed obsolete `scripts/generate_cursor_assets.py` dual source of truth.
- Version status: Production/Stable.

### Removed

- Dual-maintained plugin-root asset trees from the source repository.
- Empty `runtime/data/` and obsolete install package path.

## [1.2.0] - 2026-07-19

### Added

- Cursor plugin packaging and local plugin install CLI.

## [1.1.0] - 2026-07-19

### Added

- Merge-safe installation framework, migrations, multi-OS CI, release packaging.

## [1.0.0] - 2026-07-19

### Added

- Initial CLI, runtime controllers, Cursor assets, docs, and tests.

[2.0.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v2.0.0
[1.2.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.2.0
[1.1.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.1.0
[1.0.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.0.0
