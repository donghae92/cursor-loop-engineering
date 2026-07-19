# Changelog

All notable changes to Cursor Loop Engineering are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-19

### Added

- **Cursor Plugin packaging** — `.cursor-plugin/plugin.json`, root `rules/`, `skills/`, `agents/`, `commands/`, `hooks/`, `mcp.json`, and `assets/`.
- **Slash commands** — `cle-verify`, `cle-status`, `cle-repair`, `cle-loop`, `cle-install`, `cle-update`.
- **Plugin CLI** — `plugin-validate`, `plugin-doctor`, `plugin-install`, `plugin-update`, `plugin-remove`.
- **Local plugin install** — installs to `~/.cursor/plugins/local/cursor-loop-engineering` for Cursor `/add-plugin` discovery.
- **Marketplace docs** — `MARKETPLACE.md`, plugin installation and packaging guides.
- **Migration** — `1.1.0` → `1.2.0` upgrade/rollback scripts.

### Changed

- Installer prefers plugin-root component directories and normalizes hook command paths for project installs.

## [1.1.0] - 2026-07-19

### Added

- Merge-safe installation framework, migrations, multi-OS CI, and release packaging.

## [1.0.0] - 2026-07-19

### Added

- Initial CLI, runtime controllers, Cursor assets, docs, and tests.

### Requirements

- Python 3.9 or newer (3.11 recommended for CI).

[1.2.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.2.0
[1.1.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.1.0
[1.0.0]: https://github.com/donghae92/cursor-loop-engineering/releases/tag/v1.0.0
