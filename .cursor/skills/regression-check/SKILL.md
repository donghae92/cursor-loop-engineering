---
name: regression-check
description: Runs regression controller and interprets L1–L8 results. Use when working with Cursor Loop Engineering regression check.
---

# Regression Check

```bash
python3 -m cursor_loop verify
```

Inspect `.cursor-loop/regression_history.jsonl`. On FAIL, repair then re-run.
