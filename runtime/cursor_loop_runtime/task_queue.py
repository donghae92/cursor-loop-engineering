"""Task queue persistence and backlog promotion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import Task, TaskStatus, read_jsonl, utcnow, write_jsonl


class TaskQueue:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)
        self.paths = self.memory.paths

    def list_tasks(self) -> list[Task]:
        self.memory.ensure()
        return [Task.from_dict(row) for row in read_jsonl(self.paths.task_queue)]

    def save_tasks(self, tasks: list[Task]) -> None:
        write_jsonl(self.paths.task_queue, [task.to_dict() for task in tasks])

    def upsert(self, task: Task) -> Task:
        tasks = self.list_tasks()
        by_id = {item.task_id: item for item in tasks}
        task.updated_at = utcnow()
        by_id[task.task_id] = task
        ordered = sorted(by_id.values(), key=lambda item: item.task_id)
        self.save_tasks(ordered)
        return task

    def enqueue_backlog(self, mission: str, worker_role: str = "developer", **extra: Any) -> dict[str, Any]:
        self.memory.ensure()
        from .models import append_jsonl

        item = {
            "task_id": f"B-{utcnow()}",
            "mission": mission,
            "status": TaskStatus.BACKLOG.value,
            "worker_role": worker_role,
            "created_at": utcnow(),
            **extra,
        }
        append_jsonl(self.paths.backlog, item)
        self.memory.log_event("BACKLOG_ENQUEUE", "NOTICE", mission)
        return item

    def promote_backlog(self, limit: int = 5) -> list[Task]:
        self.memory.ensure()
        backlog = read_jsonl(self.paths.backlog)
        if not backlog:
            return []
        promoted: list[Task] = []
        remaining: list[dict[str, Any]] = []
        for index, item in enumerate(backlog):
            if index < limit:
                task = Task(
                    task_id=str(item.get("task_id") or f"B-{utcnow()}"),
                    mission=str(item.get("mission") or "backlog task"),
                    status=TaskStatus.READY.value,
                    worker_role=str(item.get("worker_role") or "developer"),
                    dependencies=list(item.get("dependencies") or []),
                    acceptance_criteria=list(item.get("acceptance_criteria") or []),
                )
                self.upsert(task)
                promoted.append(task)
            else:
                remaining.append(item)
        write_jsonl(self.paths.backlog, remaining)
        return promoted

    def mark_done(self, task_id: str) -> Task | None:
        tasks = self.list_tasks()
        for task in tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.DONE.value
                task.updated_at = utcnow()
                self.save_tasks(tasks)
                return task
        return None

    def summary(self) -> dict[str, Any]:
        tasks = self.list_tasks()
        counts: dict[str, int] = {}
        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
        return {
            "total": len(tasks),
            "counts": counts,
            "ready": [task.task_id for task in tasks if task.status == TaskStatus.READY.value],
            "blocked": [task.task_id for task in tasks if task.status == TaskStatus.BLOCKED.value],
            "done": [task.task_id for task in tasks if task.status == TaskStatus.DONE.value],
        }
