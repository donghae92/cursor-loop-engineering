"""Tests for shared runtime models and path helpers."""

from __future__ import annotations

from pathlib import Path

from cursor_loop_runtime.models import (
    Disposition,
    LoopState,
    Task,
    TaskStatus,
    WorkspacePaths,
    read_json,
    sha256_text,
    write_json_atomic,
)


def test_workspace_paths_resolve_under_root(isolated_project: Path) -> None:
    paths = WorkspacePaths(isolated_project)

    assert paths.root == isolated_project
    assert paths.cursor == isolated_project / ".cursor"
    assert paths.rules == isolated_project / ".cursor" / "rules"
    assert paths.skills == isolated_project / ".cursor" / "skills"
    assert paths.agents == isolated_project / ".cursor" / "agents"
    assert paths.hooks == isolated_project / ".cursor" / "hooks"
    assert paths.hooks_json == isolated_project / ".cursor" / "hooks.json"
    assert paths.runtime_dir == isolated_project / ".cursor-loop"
    assert paths.state == isolated_project / ".cursor-loop" / "state.json"
    assert paths.loop_state == isolated_project / ".cursor-loop" / "loop_state.json"
    assert paths.task_queue == isolated_project / ".cursor-loop" / "task_queue.jsonl"
    assert paths.checkpoints == isolated_project / ".cursor-loop" / "checkpoints"
    assert paths.quarantine == isolated_project / ".cursor-loop" / "quarantine"
    assert paths.manifest == isolated_project / ".cursor-loop" / "install_manifest.json"


def test_loop_state_roundtrip() -> None:
    original = LoopState(
        loop_id="LOOP-TEST",
        iteration=3,
        section_id="VERIFY",
        retry_budget=7,
        retries_used=2,
        last_gate="REGRESSION",
        last_result="FAIL",
        disposition=Disposition.CONTINUE.value,
        last_failure_fingerprint="abc123",
        identical_failure_count=2,
        updated_at="2026-01-01T00:00:00+00:00",
    )

    restored = LoopState.from_dict(original.to_dict())

    assert restored.loop_id == "LOOP-TEST"
    assert restored.iteration == 3
    assert restored.section_id == "VERIFY"
    assert restored.retry_budget == 7
    assert restored.retries_used == 2
    assert restored.last_gate == "REGRESSION"
    assert restored.last_result == "FAIL"
    assert restored.disposition == Disposition.CONTINUE.value
    assert restored.last_failure_fingerprint == "abc123"
    assert restored.identical_failure_count == 2
    assert restored.updated_at == "2026-01-01T00:00:00+00:00"


def test_loop_state_ignores_unknown_fields() -> None:
    data = LoopState().to_dict()
    data["unexpected_field"] = "ignored"

    restored = LoopState.from_dict(data)

    assert not hasattr(restored, "unexpected_field")


def test_task_roundtrip() -> None:
    original = Task(
        task_id="T9999",
        mission="Validate regression baseline",
        status=TaskStatus.READY.value,
        worker_role="qa",
        dependencies=["T0001"],
        acceptance_criteria=["regression history entry exists"],
        blocker=None,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-02T00:00:00+00:00",
    )

    restored = Task.from_dict(original.to_dict())

    assert restored.task_id == "T9999"
    assert restored.mission == "Validate regression baseline"
    assert restored.status == TaskStatus.READY.value
    assert restored.worker_role == "qa"
    assert restored.dependencies == ["T0001"]
    assert restored.acceptance_criteria == ["regression history entry exists"]
    assert restored.blocker is None


def test_json_helpers_roundtrip(tmp_path: Path) -> None:
    payload = {"key": "value", "count": 42}
    target = tmp_path / "nested" / "data.json"

    write_json_atomic(target, payload)
    loaded = read_json(target)

    assert loaded == payload
    assert sha256_text('{"a":1}') == sha256_text('{"a":1}')
    assert sha256_text('{"a":1}') != sha256_text('{"a":2}')
