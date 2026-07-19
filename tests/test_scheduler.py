"""Tests for scheduler queue synchronization."""

from __future__ import annotations

import json
from pathlib import Path

from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import TaskStatus, read_json
from cursor_loop_runtime.scheduler import DEFAULT_TASK_SPECS, Scheduler


def test_run_seeds_default_tasks(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    scheduler = Scheduler(isolated_project)

    result = scheduler.run()

    assert result["result"] == "PASS"
    task_ids = {task.task_id for task in scheduler.queue.list_tasks()}
    for spec in DEFAULT_TASK_SPECS:
        assert spec["task_id"] in task_ids
    assert result["summary"]["total"] == len(DEFAULT_TASK_SPECS)


def test_run_updates_t0001_done_when_cursor_and_runtime_ready(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    scheduler = Scheduler(isolated_project)

    scheduler.run()
    tasks = {task.task_id: task for task in scheduler.queue.list_tasks()}

    assert tasks["T0001"].status == TaskStatus.DONE.value
    assert tasks["T0002"].status == TaskStatus.READY.value
    assert tasks["T0003"].status == TaskStatus.WAITING.value
    assert tasks["T0004"].status == TaskStatus.WAITING.value


def test_run_marks_t0002_done_when_verify_artifact_exists(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    verify_path = memory.paths.runtime_dir / "last_verify.json"
    verify_path.write_text(
        json.dumps({"result": "PASS", "failures": []}) + "\n",
        encoding="utf-8",
    )

    scheduler = Scheduler(isolated_project)
    scheduler.run()
    tasks = {task.task_id: task for task in scheduler.queue.list_tasks()}

    assert tasks["T0001"].status == TaskStatus.DONE.value
    assert tasks["T0002"].status == TaskStatus.DONE.value
    assert tasks["T0003"].status == TaskStatus.READY.value
    assert tasks["T0004"].status == TaskStatus.WAITING.value


def test_run_increments_schedule_runs(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    scheduler = Scheduler(isolated_project)
    perf_before = read_json(scheduler.memory.paths.performance, {})
    before = int(perf_before.get("schedule_runs", 0))

    scheduler.run()
    scheduler.run()

    perf = read_json(scheduler.memory.paths.performance, {})
    # Each run increments schedule_runs twice: record_timing + explicit counter.
    assert perf["schedule_runs"] == before + 4
