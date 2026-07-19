"""Tests for checkpoint create, list, restore, and verify."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cursor_loop_runtime.checkpoint_manager import CheckpointManager
from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import read_json, write_json_atomic


def test_create_checkpoint_copies_runtime_files(bootstrapped_project: Path) -> None:
    memory = MemoryController(bootstrapped_project)
    memory.update_state(note="checkpoint-source")
    manager = CheckpointManager(bootstrapped_project)

    meta = manager.create("unit-test")

    assert meta["label"] == "unit-test"
    assert "state.json" in meta["files"]
    checkpoint_dir = memory.paths.checkpoints / meta["checkpoint_id"]
    assert checkpoint_dir.exists()
    assert (checkpoint_dir / "checkpoint.json").exists()
    assert (checkpoint_dir / "state.json").exists()


def test_list_checkpoints_returns_created_entries(bootstrapped_project: Path) -> None:
    manager = CheckpointManager(bootstrapped_project)
    first = manager.create("first")
    second = manager.create("second")

    rows = manager.list_checkpoints()

    checkpoint_ids = {row["checkpoint_id"] for row in rows}
    assert first["checkpoint_id"] in checkpoint_ids
    assert second["checkpoint_id"] in checkpoint_ids


def test_restore_replaces_runtime_files(bootstrapped_project: Path) -> None:
    memory = MemoryController(bootstrapped_project)
    manager = CheckpointManager(bootstrapped_project)
    meta = manager.create("before-change")
    memory.update_state(note="changed-after-checkpoint")

    restored = manager.restore(meta["checkpoint_id"])
    state = read_json(memory.paths.state, {})

    assert restored["result"] == "PASS"
    assert restored["checkpoint_id"] == meta["checkpoint_id"]
    assert "state.json" in restored["restored"]
    assert state.get("note") != "changed-after-checkpoint"


def test_verify_checkpoint_passes_for_intact_snapshot(bootstrapped_project: Path) -> None:
    manager = CheckpointManager(bootstrapped_project)
    meta = manager.create("verify-me")

    result = manager.verify_checkpoint(meta["checkpoint_id"])

    assert result["result"] == "PASS"
    assert result["checkpoint_id"] == meta["checkpoint_id"]
    assert result["missing"] == []
    assert len(result["meta_hash"]) == 64


def test_verify_checkpoint_fails_when_file_missing(bootstrapped_project: Path) -> None:
    memory = MemoryController(bootstrapped_project)
    manager = CheckpointManager(bootstrapped_project)
    meta = manager.create("broken")
    checkpoint_dir = memory.paths.checkpoints / meta["checkpoint_id"]
    (checkpoint_dir / "state.json").unlink()

    result = manager.verify_checkpoint(meta["checkpoint_id"])

    assert result["result"] == "FAIL"
    assert "state.json" in result["missing"]


def test_restore_missing_checkpoint_raises(bootstrapped_project: Path) -> None:
    manager = CheckpointManager(bootstrapped_project)

    with pytest.raises(FileNotFoundError, match="checkpoint not found"):
        manager.restore("CP-does-not-exist")
