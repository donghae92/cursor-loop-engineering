---
name: cle-verify
description: Verify Cursor Loop Engineering installation and gates
---

# cle-verify

Run the canonical verification gate.

```bash
cle verify --path .
# or
python3 -m cursor_loop verify --path .
```

Expect JSON with `"result": "PASS"` and an empty `failures` list.
