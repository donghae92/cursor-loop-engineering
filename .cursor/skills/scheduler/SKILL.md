---
name: scheduler
description: Synchronizes the task queue and promotes backlog items. Use when working with Cursor Loop Engineering scheduler.
---

# Scheduler

Use the scheduler via status/repair flows or Python:

```python
from cursor_loop_runtime.scheduler import Scheduler
Scheduler().run()
```
