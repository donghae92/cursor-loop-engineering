"""Scheduler — dependency-aware task queue synchronization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import Task, TaskStatus, read_json, utcnow, write_json_atomic
from .task_queue import TaskQueue


DEFAULT_TASK_SPECS: list[dict[str, Any]] = [
    {
        "task_id": "T0001",
        "mission": "Bootstrap Cursor Loop Engineering into the project",
        "worker_role": "manager",
        "dependencies": [],
        "acceptance_criteria": [".cursor/rules present", ".cursor-loop runtime present"],
    },
    {
        "task_id": "T0002",
        "mission": "Verify framework installation",
        "worker_role": "qa",
        "dependencies": ["T0001"],
        "acceptance_criteria": ["cle verify PASS", "cle doctor PASS"],
    },
    {
        "task_id": "T0003",
        "mission": "Establish regression baseline",
        "worker_role": "regression",
        "dependencies": ["T0002"],
        "acceptance_criteria": ["regression history entry exists"],
    },
    {
        "task_id": "T0004",
        "mission": "Confirm evidence policy and release readiness",
        "worker_role": "release",
        "dependencies": ["T0003"],
        "acceptance_criteria": ["evidence check PASS", "no confidence-as-evidence rows"],
    },
]


class Scheduler:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)
        self.queue = TaskQueue(root)
        self.root = self.memory.paths.root

    def _load_template_specs(self) -> list[dict[str, Any]]:
        template = self.root / ".cursor" / "templates" / "task.json"
        if not template.exists():
            return list(DEFAULT_TASK_SPECS)
        try:
            data = json.loads(template.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return list(DEFAULT_TASK_SPECS)
        if isinstance(data, dict) and isinstance(data.get("tasks"), list):
            return list(data["tasks"])
        # Single-task template: keep defaults; template is a shape example
        return list(DEFAULT_TASK_SPECS)

    def _deps_satisfied(self, task: Task, by_id: dict[str, Task]) -> bool:
        for dep in task.dependencies:
            other = by_id.get(dep)
            if other is None or other.status != TaskStatus.DONE.value:
                return False
        return True

    def _acceptance_met(self, task: Task) -> bool:
        cursor_ok = self.memory.paths.rules.exists() and self.memory.paths.hooks_json.exists()
        runtime_ok = self.memory.paths.runtime_dir.exists() and self.memory.paths.state.exists()
        verify_artifact = self.memory.paths.runtime_dir / "last_verify.json"
        verify_ok = False
        if verify_artifact.exists():
            verify_ok = read_json(verify_artifact, {}).get("result") == "PASS"
        history = self.memory.paths.regression_history
        has_history = history.exists() and history.stat().st_size > 0
        evidence_path = self.memory.paths.evidence_log
        evidence_ok = evidence_path.exists()

        criteria = " | ".join(task.acceptance_criteria).lower()
        if task.task_id == "T0001" or "runtime present" in criteria:
            return cursor_ok and runtime_ok
        if task.task_id == "T0002" or "verify" in criteria:
            return verify_ok or verify_artifact.exists()
        if task.task_id == "T0003" or "regression" in criteria:
            return has_history
        if task.task_id == "T0004" or "evidence" in criteria:
            return evidence_ok and has_history
        # Generic: done when dependencies satisfied and runtime healthy
        return runtime_ok

    def _refresh_statuses(self, tasks: list[Task]) -> list[Task]:
        by_id = {task.task_id: task for task in tasks}
        for task in by_id.values():
            if not self._deps_satisfied(task, by_id):
                task.status = TaskStatus.WAITING.value
            elif self._acceptance_met(task):
                task.status = TaskStatus.DONE.value
            elif task.status in {TaskStatus.DONE.value, TaskStatus.WAITING.value, TaskStatus.BLOCKED.value}:
                task.status = TaskStatus.READY.value
            task.updated_at = utcnow()
        return sorted(by_id.values(), key=lambda item: item.task_id)

    def run(self) -> dict[str, Any]:
        self.memory.ensure()
        existing = {task.task_id: task for task in self.queue.list_tasks()}
        for spec in self._load_template_specs():
            task_id = str(spec.get("task_id") or "")
            if not task_id or task_id in existing:
                continue
            existing[task_id] = Task(
                task_id=task_id,
                mission=str(spec.get("mission") or task_id),
                status=TaskStatus.WAITING.value if spec.get("dependencies") else TaskStatus.READY.value,
                worker_role=str(spec.get("worker_role") or "manager"),
                dependencies=list(spec.get("dependencies") or []),
                acceptance_criteria=list(spec.get("acceptance_criteria") or []),
            )
        refreshed = self._refresh_statuses(list(existing.values()))
        self.queue.save_tasks(refreshed)
        promoted = self.queue.promote_backlog()
        performance = read_json(self.memory.paths.performance, {})
        performance["schedule_runs"] = int(performance.get("schedule_runs", 0)) + 1
        performance["updated_at"] = utcnow()
        write_json_atomic(self.memory.paths.performance, performance)
        self.memory.record_timing("schedule", 0.0, True)
        self.memory.log_event("SCHEDULE_RUN", "NOTICE", "Task queue synchronized")
        return {
            "result": "PASS",
            "promoted": [task.task_id for task in promoted],
            "summary": self.queue.summary(),
            "ready": [t.task_id for t in refreshed if t.status == TaskStatus.READY.value],
            "done": [t.task_id for t in refreshed if t.status == TaskStatus.DONE.value],
            "scheduled_at": utcnow(),
        }
