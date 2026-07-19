---
name: cle-loop
description: Advance or inspect the Cursor Loop Engineering failed-section loop
---

# Loop

```bash
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop loop --status
PYTHONPATH=sdk:runtime:install python3 -m cursor_loop loop --once
```

Continue only while disposition is CONTINUE and measurable progress exists. Otherwise SAFE_STOP or MANUAL_REVIEW.
