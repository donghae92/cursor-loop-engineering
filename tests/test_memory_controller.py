"""Tests for MemoryController durable runtime memory."""

from __future__ import annotations

import json
from pathlib import Path

from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import LoopState, read_json, read_jsonl


def test_ensure_creates_runtime_artifacts(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    created = memory.ensure()

    assert created["runtime_dir"] == str(isolated_project / ".cursor-loop")
    assert (isolated_project / ".cursor-loop" / "state.json").exists()
    assert (isolated_project / ".cursor-loop" / "loop_state.json").exists()
    assert (isolated_project / ".cursor-loop" / "performance.json").exists()
    assert (isolated_project / ".cursor-loop" / "events.jsonl").exists()
    assert (isolated_project / ".cursor-loop" / "checkpoints").is_dir()
    assert (isolated_project / ".cursor-loop" / "quarantine").is_dir()


def test_log_event_appends_to_events(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)

    event = memory.log_event("TEST_EVENT", "NOTICE", "hello", detail="extra")

    assert event["event_type"] == "TEST_EVENT"
    assert event["severity"] == "NOTICE"
    assert event["message"] == "hello"
    assert event["detail"] == "extra"
    rows = read_jsonl(memory.paths.events)
    assert len(rows) == 1
    assert rows[0]["event_id"] == event["event_id"]


def test_append_decision_records_history(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)

    record = memory.append_decision("UNIT_TEST", "OK", "decision rationale", gate="VERIFY")

    assert record["decision_type"] == "UNIT_TEST"
    assert record["result"] == "OK"
    assert record["gate"] == "VERIFY"
    rows = read_jsonl(memory.paths.decision_history)
    assert len(rows) == 1
    assert rows[0]["decision_id"] == record["decision_id"]


def test_record_timing_updates_performance(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)

    perf = memory.record_timing("validate", 100.0, True)
    assert perf["validate_runs"] == 1
    assert perf["validate_pass"] == 1
    assert perf["validate_fail"] == 0
    assert perf["avg_validate_ms"] == 100.0

    perf = memory.record_timing("validate", 200.0, False)
    assert perf["validate_runs"] == 2
    assert perf["validate_pass"] == 1
    assert perf["validate_fail"] == 1
    assert perf["avg_validate_ms"] == 150.0


def test_state_and_loop_state_persistence(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()

    updated = memory.update_state(phase="HEALTHY", health="HEALTHY", note="test")
    assert updated["phase"] == "HEALTHY"
    assert updated["health"] == "HEALTHY"
    assert updated["note"] == "test"
    assert "updated_at" in updated

    loaded = memory.get_state()
    assert loaded["phase"] == "HEALTHY"

    loop_state = memory.get_loop_state()
    assert isinstance(loop_state, LoopState)
    assert loop_state.loop_id == "LOOP-V1"

    loop_state.iteration = 5
    saved = memory.save_loop_state(loop_state)
    assert saved.iteration == 5
    reloaded = json.loads((isolated_project / ".cursor-loop" / "loop_state.json").read_text())
    assert reloaded["iteration"] == 5
