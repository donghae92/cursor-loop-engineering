"""Tests for loop controller gate results and stop dispositions."""

from __future__ import annotations

from pathlib import Path

from cursor_loop_runtime.loop_controller import LoopController
from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import Disposition, read_json, write_json_atomic


def test_mark_gate_result_pass_resets_loop(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    controller = LoopController(isolated_project)

    state = controller.mark_gate_result("VERIFY", True, section_id="VERIFY")

    assert state.last_result == "PASS"
    assert state.last_gate == "VERIFY"
    assert state.disposition == Disposition.IDLE.value
    assert state.retries_used == 0
    assert state.identical_failure_count == 0
    assert state.last_failure_fingerprint is None


def test_mark_gate_result_fail_sets_continue(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    controller = LoopController(isolated_project)

    state = controller.mark_gate_result("VERIFY", False, failures=["missing rule"])

    assert state.last_result == "FAIL"
    assert state.disposition == Disposition.CONTINUE.value
    assert state.retries_used == 1
    assert state.identical_failure_count == 1
    assert state.last_failure_fingerprint is not None


def test_identical_failure_triggers_safe_stop(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    controller = LoopController(isolated_project)
    failures = ["same failure signature"]

    state = controller.mark_gate_result("VERIFY", False, failures=failures)
    assert state.disposition == Disposition.CONTINUE.value

    state = controller.mark_gate_result("VERIFY", False, failures=failures)
    assert state.disposition == Disposition.CONTINUE.value

    state = controller.mark_gate_result("VERIFY", False, failures=failures)
    assert state.disposition == Disposition.SAFE_STOP.value
    assert state.identical_failure_count == 3


def test_retry_budget_exhaustion_triggers_manual_review(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    controller = LoopController(isolated_project)
    loop_state = memory.get_loop_state()
    loop_state.retry_budget = 2
    memory.save_loop_state(loop_state)

    controller.mark_gate_result("VERIFY", False, failures=["failure-a"])
    controller.mark_gate_result("VERIFY", False, failures=["failure-b"])
    state = controller.mark_gate_result("VERIFY", False, failures=["failure-c"])

    assert state.disposition == Disposition.MANUAL_REVIEW.value
    assert state.retries_used == 3


def test_run_once_reads_last_verify(isolated_project: Path) -> None:
    memory = MemoryController(isolated_project)
    memory.ensure()
    write_json_atomic(
        memory.paths.runtime_dir / "last_verify.json",
        {"result": "FAIL", "failures": ["regression failed"]},
    )
    controller = LoopController(isolated_project)

    out = controller.run_once()

    assert out["verification_result"] == "FAIL"
    assert out["loop_state"]["last_result"] == "FAIL"
    assert out["loop_state"]["disposition"] == Disposition.CONTINUE.value
    assert out["localization"]["primary_section"]
    assert out["repair"] is not None


def test_fingerprint_failure_is_stable(isolated_project: Path) -> None:
    controller = LoopController(isolated_project)

    first = controller.fingerprint_failure("GATE", ["b", "a"])
    second = controller.fingerprint_failure("GATE", ["a", "b"])

    assert first == second
