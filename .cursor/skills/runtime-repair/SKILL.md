---
name: runtime-repair
description: Diagnoses degraded Cursor Loop runtime and repairs install/runtime artifacts. Use when working with Cursor Loop Engineering runtime repair.
---

# Runtime Repair

1. `python3 -m cursor_loop status`
2. `python3 -m cursor_loop doctor`
3. `python3 -m cursor_loop repair`
4. Re-run `python3 -m cursor_loop verify`

Stop on SAFE_STOP / MANUAL_REVIEW or when source mutation outside the project is required.
