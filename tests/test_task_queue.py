"""Tests for task queue persistence and backlog promotion."""

from __future__ import annotations

from pathlib import Path

from cursor_loop_runtime.models import Task, TaskStatus
from cursor_loop_runtime.task_queue import TaskQueue


def test_upsert_creates_and_updates_tasks(isolated_project: Path) -> None:
    queue = TaskQueue(isolated_project)

    created = queue.upsert(
        Task(task_id="T100", mission="First mission", status=TaskStatus.READY.value)
    )
    assert created.task_id == "T100"
    assert created.mission == "First mission"

    updated = queue.upsert(
        Task(task_id="T100", mission="Updated mission", status=TaskStatus.RUNNING.value)
    )
    tasks = queue.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].mission == "Updated mission"
    assert tasks[0].status == TaskStatus.RUNNING.value


def test_upsert_sorts_by_task_id(isolated_project: Path) -> None:
    queue = TaskQueue(isolated_project)
    queue.upsert(Task(task_id="T200", mission="second"))
    queue.upsert(Task(task_id="T100", mission="first"))

    task_ids = [task.task_id for task in queue.list_tasks()]
    assert task_ids == ["T100", "T200"]


def test_promote_backlog_moves_items_to_queue(isolated_project: Path) -> None:
    queue = TaskQueue(isolated_project)

    queue.enqueue_backlog("Backlog item one", worker_role="developer")
    queue.enqueue_backlog("Backlog item two", worker_role="qa")

    promoted = queue.promote_backlog(limit=2)

    assert len(promoted) == 2
    assert all(task.status == TaskStatus.READY.value for task in promoted)
    tasks = queue.list_tasks()
    assert len(tasks) == 2
    assert queue.summary()["total"] == 2


def test_mark_done_updates_status(isolated_project: Path) -> None:
    queue = TaskQueue(isolated_project)
    queue.upsert(Task(task_id="T300", mission="finish me", status=TaskStatus.READY.value))

    done = queue.mark_done("T300")

    assert done is not None
    assert done.status == TaskStatus.DONE.value
    assert queue.mark_done("missing") is None


def test_summary_counts_by_status(isolated_project: Path) -> None:
    queue = TaskQueue(isolated_project)
    queue.upsert(Task(task_id="T401", mission="ready", status=TaskStatus.READY.value))
    queue.upsert(Task(task_id="T402", mission="blocked", status=TaskStatus.BLOCKED.value))
    queue.upsert(Task(task_id="T403", mission="done", status=TaskStatus.DONE.value))

    summary = queue.summary()

    assert summary["total"] == 3
    assert summary["counts"][TaskStatus.READY.value] == 1
    assert summary["counts"][TaskStatus.BLOCKED.value] == 1
    assert summary["counts"][TaskStatus.DONE.value] == 1
    assert summary["ready"] == ["T401"]
    assert summary["blocked"] == ["T402"]
    assert summary["done"] == ["T403"]
