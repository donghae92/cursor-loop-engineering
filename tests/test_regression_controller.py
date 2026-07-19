"""Tests for regression controller schema and hash checks."""

from __future__ import annotations

import json
from pathlib import Path

from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import read_jsonl, sha256_file, write_json_atomic
from cursor_loop_runtime.regression_controller import RegressionController


def test_l1_fails_without_hooks_json(tmp_path: Path) -> None:
    MemoryController(tmp_path).ensure()
    controller = RegressionController(tmp_path)

    failures = controller.check_l1_schema()

    assert any("missing .cursor/hooks.json" in item for item in failures)


def test_l1_passes_with_valid_hooks_json(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    controller = RegressionController(isolated_project)

    failures = controller.check_l1_schema()

    assert failures == []


def test_l1_fails_with_invalid_hooks_version(isolated_project: Path) -> None:
    hooks = isolated_project / ".cursor" / "hooks.json"
    hooks.write_text(
        json.dumps({"version": 2, "hooks": {}}) + "\n",
        encoding="utf-8",
    )
    MemoryController(isolated_project).ensure()
    controller = RegressionController(isolated_project)

    failures = controller.check_l1_schema()

    assert any("version must be 1" in item for item in failures)


def test_run_passes_with_minimal_hooks(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    controller = RegressionController(isolated_project)

    record = controller.run()

    assert record["result"] == "PASS"
    assert record["levels"]["L1_SCHEMA"] == "PASS"
    assert record["levels"]["L2_HASH"] == "PASS"
    assert record["levels"]["L3_PROVENANCE"] == "PASS"
    assert record["levels"]["L4_SEMANTIC"] == "PASS"
    assert record["levels"]["L5_TEMPORAL"] == "PASS"
    assert record["levels"]["L6_DEPENDENCY"] == "PASS"
    assert record["levels"]["L7_REPRESENTATIVE"] == "PASS"
    assert record["levels"]["L8_BOOT"] == "PASS"
    assert record["failure_count"] == 0
    history = read_jsonl(controller.memory.paths.regression_history)
    assert len(history) == 1
    assert history[0]["result"] == "PASS"


def test_run_fails_without_hooks_json(tmp_path: Path) -> None:
    MemoryController(tmp_path).ensure()
    controller = RegressionController(tmp_path)

    record = controller.run()

    assert record["result"] == "FAIL"
    assert record["levels"]["L1_SCHEMA"] == "FAIL"
    assert record["failure_count"] > 0


def test_l2_hash_detects_manifest_mismatch(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    hooks_path = isolated_project / ".cursor" / "hooks.json"
    write_json_atomic(
        memory.paths.manifest,
        {
            "files": [
                {
                    "path": ".cursor/hooks.json",
                    "sha256": "0" * 64,
                }
            ]
        },
    )
    controller = RegressionController(isolated_project)

    failures = controller.check_l2_hash()

    assert any("hash mismatch" in item for item in failures)
    assert sha256_file(hooks_path) != "0" * 64
