"""Scheduler — synchronize queue and seed default engineering tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import Task, TaskStatus, utcnow
from .task_queue import TaskQueue


DEFAULT_TASKS = [
    Task(
        task_id="T0001",
        mission="Bootstrap Cursor Loop Engineering into the project",
        status=TaskStatus.READY.value,
        worker_role="manager",
        acceptance_criteria=[".cursor/rules present", ".cursor-loop runtime present"],
    ),
    Task(
        task_id="T0002",
        mission="Verify framework installation",
        status=TaskStatus.WAITING.value,
        worker_role="qa",
        dependencies=["T0001"],
        acceptance_criteria=["cle verify PASS", "cle doctor PASS"],
    ),
    Task(
        task_id="T0003",
        mission="Establish regression baseline",
        status=TaskStatus.WAITING.value,
        worker_role="regression",
        dependencies=["T0002"],
        acceptance_criteria=["regression history entry exists"],
    ),
]


class Scheduler:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)
        self.queue = TaskQueue(root)

    def _refresh_statuses(self, tasks: list[Task]) -> list[Task]:
        by_id = {task.task_id: task for task in tasks}
        cursor_ok = self.memory.paths.rules.exists() and self.memory.paths.hooks_json.exists()
        runtime_ok = self.memory.paths.runtime_dir.exists() and self.memory.paths.state.exists()

        if "T0001" in by_id:
            by_id["T0001"].status = TaskStatus.DONE.value if cursor_ok and runtime_ok else TaskStatus.READY.value
        if "T0002" in by_id:
            if by_id.get("T0001") and by_id["T0001"].status == TaskStatus.DONE.value:
                verify_artifact = self.memory.paths.runtime_dir / "last_verify.json"
                by_id["T0002"].status = (
                    TaskStatus.DONE.value if verify_artifact.exists() else TaskStatus.READY.value
                )
            else:
                by_id["T0002"].status = TaskStatus.WAITING.value
        if "T0003" in by_id:
            history = self.memory.paths.regression_history
            has_history = history.exists() and history.stat().st_size > 0
            if by_id.get("T0002") and by_id["T0002"].status == TaskStatus.DONE.value:
                by_id["T0003"].status = TaskStatus.DONE.value if has_history else TaskStatus.READY.value
            else:
                by_id["T0003"].status = TaskStatus.WAITING.value

        for task in by_id.values():
            task.updated_at = utcnow()
        return sorted(by_id.values(), key=lambda item: item.task_id)

    def run(self) -> dict[str, Any]:
        self.memory.ensure()
        existing = {task.task_id: task for task in self.queue.list_tasks()}
        for default in DEFAULT_TASKS:
            if default.task_id not in existing:
                existing[default.task_id] = default
        refreshed = self._refresh_statuses(list(existing.values()))
        self.queue.save_tasks(refreshed)
        promoted = self.queue.promote_backlog()
        self.memory.record_timing("schedule", 0.0, True)
        perf = self.memory.get_state()
        _ = perf
        from .models import read_json, write_json_atomic

        performance = read_json(self.memory.paths.performance, {})
        performance["schedule_runs"] = int(performance.get("schedule_runs", 0)) + 1
        performance["updated_at"] = utcnow()
        write_json_atomic(self.memory.paths.performance, performance)
        self.memory.log_event("SCHEDULE_RUN", "NOTICE", "Task queue synchronized")
        summary = self.queue.summary()
        return {
            "result": "PASS",
            "promoted": [task.task_id for task in promoted],
            "summary": summary,
            "scheduled_at": utcnow(),
        }
