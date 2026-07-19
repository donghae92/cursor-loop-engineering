"""Tests for evidence controller validation and quarantine."""

from __future__ import annotations

from pathlib import Path

import pytest

from cursor_loop_runtime.evidence_controller import EvidenceController
from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import append_jsonl, read_jsonl


def test_record_rejects_confidence_evidence(isolated_project: Path) -> None:
    controller = EvidenceController(isolated_project)

    with pytest.raises(ValueError, match="INSUFFICIENT_EVIDENCE"):
        controller.record("CONFIDENCE", "model", "likely correct")

    with pytest.raises(ValueError, match="INSUFFICIENT_EVIDENCE"):
        controller.record("MODEL_CONFIDENCE", "model", "likely correct")


def test_record_accepts_file_evidence(isolated_project: Path) -> None:
    controller = EvidenceController(isolated_project)

    record = controller.record("FILE_HASH", ".cursor/hooks.json", "hooks present")

    assert record["evidence_class"] == "FILE_HASH"
    rows = read_jsonl(controller.memory.paths.evidence_log)
    assert len(rows) == 1
    assert rows[0]["evidence_id"] == record["evidence_id"]


def test_check_reports_missing_required_paths(tmp_path: Path) -> None:
    MemoryController(tmp_path).ensure()
    controller = EvidenceController(tmp_path)

    result = controller.check()

    assert result["result"] == "FAIL"
    assert ".cursor/hooks.json" in result["missing"]


def test_check_reports_confidence_violations(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    append_jsonl(
        memory.paths.evidence_log,
        {
            "evidence_id": "EVD-BAD",
            "evidence_class": "CONFIDENCE",
            "path": "model",
            "claim": "probably fine",
        },
    )
    controller = EvidenceController(isolated_project)

    result = controller.check()

    assert result["result"] == "FAIL"
    assert "EVD-BAD" in result["confidence_violations"]


def test_check_passes_with_valid_project(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    controller = EvidenceController(isolated_project)

    result = controller.check()

    assert result["result"] == "PASS"
    assert result["missing"] == []
    assert result["confidence_violations"] == []


def test_quarantine_moves_file_into_quarantine_dir(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    suspect = isolated_project / "suspect.txt"
    suspect.write_text("ambiguous output", encoding="utf-8")
    controller = EvidenceController(isolated_project)

    result = controller.quarantine(suspect, "ambiguous evidence")

    assert result["result"] == "PASS"
    assert not suspect.exists()
    quarantined = Path(result["quarantined_to"])
    assert quarantined.exists()
    assert quarantined.parent == memory.paths.quarantine
    assert quarantined.read_text(encoding="utf-8") == "ambiguous output"


def test_quarantine_missing_file_fails(isolated_project: Path) -> None:
    controller = EvidenceController(isolated_project)

    result = controller.quarantine(isolated_project / "missing.txt", "not found")

    assert result["result"] == "FAIL"
    assert "missing" in result["reason"]
