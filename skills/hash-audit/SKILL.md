---
name: hash-audit
description: Audits install manifest hashes against on-disk Cursor assets. Use when working with Cursor Loop Engineering hash audit.
---

# Hash Audit

Regression L2 compares `.cursor-loop/install_manifest.json` hashes.
On mismatch, run `python3 -m cursor_loop update` then verify.
