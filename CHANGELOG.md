# Changelog

All notable changes to Cursor Loop Engineering are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-19

### Added

- **Reusable installation framework** — merge-safe install/update into empty, existing, monorepo, small, and large projects.
- **Installer package** — `install/cursor_loop_install` with detect, backup, merge, verify, doctor, export/import, remove, and migration engine.
- **VERSION / COMPATIBILITY.json** — semantic versioning and compatibility matrix.
- **Migrations** — `migration/` registry with upgrade and rollback scripts (`1.0.0` → `1.1.0`).
- **CLI** — `remove`, `export`, `import`, `rollback`; doctor `--repair`; update preserves customizations.
- **Release workflow** — tag-driven GitHub Release packaging with checksums.
- **CI** — Linux, macOS, and Windows matrix.
- **Docs** — upgrade, compatibility, and troubleshooting guides.

### Changed

- Installer never overwrites without writing a backup under `.cursor-loop/backups/`.
- `hooks.json` merges event entries instead of blind replace.

## [1.0.0] - 2026-07-19

### Added

- Initial CLI, runtime controllers, Cursor assets, docs, and tests.

### Requirements

- Python 3.9 or newer (3.11 recommended for CI).

[1.1.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.1.0
[1.0.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.0.0
