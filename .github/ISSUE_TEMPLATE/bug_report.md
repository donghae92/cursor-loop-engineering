---
name: Bug report
about: Report a defect in Cursor Loop Engineering
title: "[Bug] "
labels: bug
assignees: ''
---

## Description

<!-- Clear description of the bug -->

## Steps to reproduce

1.
2.
3.

## Expected behavior

<!-- What should happen -->

## Actual behavior

<!-- What happened instead -->

## Environment

- **OS**:
- **Python version**: (`python3 --version`)
- **Framework version**: (`python3 -c "import importlib.metadata as m; print(m.version('cursor-loop-engineering'))"` or git commit)
- **Install method**: pip editable / `scripts/cle` / other

## Verify / doctor output

```bash
python3 -m cursor_loop doctor
python3 -m cursor_loop verify
```

```json
<!-- Paste relevant JSON stdout (redact paths if needed) -->
```

## Additional context

<!-- Logs from .cursor-loop/events.jsonl, hook errors, etc. -->
