# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 2.0.x   | Yes       |
| 1.2.x   | Security fixes only |
| 1.1.x   | No        |
| 1.0.x   | No        |
| < 1.0   | No        |

## Reporting a vulnerability

If you discover a security issue in Cursor Loop Engineering, report it responsibly.

**Do not** open a public GitHub issue for exploitable vulnerabilities.

Preferred channels (in order):

1. **GitHub Security Advisories** for [donghae92/cursor-loop-engineering](https://github.com/donghae92/cursor-loop-engineering/security/advisories/new)
2. Contact the repository owner via GitHub (@donghae92) with the subject `SECURITY: cursor-loop-engineering`

Include:

1. A description of the issue and potential impact
2. Steps to reproduce
3. Affected version(s)
4. Any suggested mitigation (optional)

We aim to acknowledge reports within **72 hours** and provide a status update within **7 days**.

## Scope

In scope:

- The `cursor_loop` / `cle` CLI and install pipeline
- Runtime controllers under `runtime/cursor_loop_runtime/`
- Installer under `sdk/cursor_loop_install/`
- Hook scripts under `.cursor/hooks/` (command injection, unsafe shell patterns)
- Integrity of install manifests and regression baselines
- Local plugin install under `~/.cursor/plugins/local/`

Out of scope:

- Vulnerabilities in upstream Cursor IDE itself (report to Cursor)
- Issues in consumer project code after framework install
- Social engineering or physical access scenarios

## Safe defaults

- **Fail closed** — Failed verification blocks release checkpoints.
- **No secrets in repo** — Never commit tokens, credentials, or `.env` files.
- **Runtime isolation** — Derived state lives under `.cursor-loop/`.
- **Executable hooks** — Hook scripts are Python-only; review changes to `.cursor/hooks/` carefully.
- **Unsafe pattern denial** — `pre_task` / `validation` hooks deny destructive shell patterns and secret-like material when detected.

## Hook safety

Hook scripts receive JSON on stdin and must emit JSON on stdout. When extending hooks:

- Avoid shelling out with unsanitized user input
- Do not embed secrets in hook output
- Keep execution under the `timeout` declared for each entry in `.cursor/hooks.json`

Run `python3 -m cursor_loop doctor` to detect missing executables or invalid `hooks.json`.

## Dependency policy

The core package declares **no runtime Python dependencies** in `pyproject.toml`. Development dependencies (pytest, etc.) are optional. Review any new dependency for supply-chain risk before merging.

## Disclosure

After a fix is available, we will:

1. Publish a patched release
2. Document the issue in CHANGELOG with credit to the reporter (unless anonymity is requested)
3. Coordinate disclosure timing with the reporter

Thank you for helping keep Cursor Loop Engineering safe for all projects.
