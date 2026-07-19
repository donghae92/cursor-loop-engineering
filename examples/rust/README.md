# Rust project example

Install Cursor Loop Engineering into a **Cargo** workspace or binary crate.

## Prerequisites

- Rust toolchain (`rustc --version`)
- Python 3.10+
- Clone of [cursor-loop-engineering](https://github.com/your-org/cursor-loop-engineering)

## Install

```bash
export CLE_ROOT="$HOME/src/cursor-loop-engineering"
pip install -e "$CLE_ROOT"

cd ~/projects/my-rust-crate

python3 -m cursor_loop install .
python3 -m cursor_loop bootstrap
python3 -m cursor_loop verify
python3 -m cursor_loop status
```

## Project layout

```
my-rust-crate/
├── .cursor/
├── .cursor-loop/
├── Cargo.toml
├── src/
└── AGENTS.md
```

## Customize `AGENTS.md`

```markdown
## Rust commands

cargo fmt --all
cargo clippy --all-targets -- -D warnings
cargo test
```

## Cursor rules

`.cursor/rules/rust.mdc`:

```yaml
---
description: Rust error handling and testing standards
globs: "**/*.rs"
alwaysApply: false
---

# Rust

- Use `thiserror` or `anyhow` consistently per crate policy.
- Run `cargo test` before review.
```

## Development loop

```bash
cargo test
python3 -m cursor_loop verify
python3 -m cursor_loop loop --status
```

On clippy or test failures, fix code then:

```bash
python3 -m cursor_loop repair
python3 -m cursor_loop verify
python3 -m cursor_loop loop --once
```

## CI

```yaml
- uses: actions-rs/toolchain@v1
  with:
    toolchain: stable
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
- run: pip install -e ./cursor-loop-engineering
- run: cargo test
- run: python3 -m cursor_loop bootstrap
- run: python3 -m cursor_loop verify
```

## Workspace members

For workspaces, install at the workspace root containing `Cargo.toml` `[workspace]`:

```bash
python3 -m cursor_loop install ~/projects/my-workspace
python3 -m cursor_loop bootstrap --path ~/projects/my-workspace
```

## Update framework

```bash
python3 -m cursor_loop update
python3 -m cursor_loop verify
```

See [docs/migration-guide.md](../../docs/migration-guide.md).
