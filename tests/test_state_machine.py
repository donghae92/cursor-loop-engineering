"""Tests for runtime phase state machine transitions."""

from __future__ import annotations

from pathlib import Path

import pytest

from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import RuntimePhase
from cursor_loop_runtime.state_machine import StateMachine


def test_current_phase_after_bootstrap(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    machine = StateMachine(isolated_project)

    assert machine.current() == RuntimePhase.BOOTSTRAPPED.value


def test_legal_transitions(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    machine = StateMachine(isolated_project)

    assert machine.can_transition(RuntimePhase.HEALTHY.value) is True
    updated = machine.transition(RuntimePhase.HEALTHY.value, "unit test healthy")
    assert updated["phase"] == RuntimePhase.HEALTHY.value
    assert machine.current() == RuntimePhase.HEALTHY.value

    assert machine.can_transition(RuntimePhase.DEGRADED.value) is True
    machine.transition(RuntimePhase.DEGRADED.value, "unit test degraded")
    assert machine.current() == RuntimePhase.DEGRADED.value

    assert machine.can_transition(RuntimePhase.REPAIRING.value) is True
    machine.transition(RuntimePhase.REPAIRING.value, "unit test repairing")
    assert machine.current() == RuntimePhase.REPAIRING.value


def test_mark_healthy_from_bootstrapped(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    machine = StateMachine(isolated_project)

    result = machine.mark_healthy("verification passed")

    assert result["phase"] == RuntimePhase.HEALTHY.value
    assert machine.current() == RuntimePhase.HEALTHY.value


def test_illegal_transition_raises(isolated_project: Path) -> None:
    MemoryController(isolated_project).ensure()
    machine = StateMachine(isolated_project)
    machine.mark_healthy("setup")

    with pytest.raises(ValueError, match="Illegal transition"):
        machine.transition(RuntimePhase.UNINITIALIZED.value, "invalid rollback")

    with pytest.raises(ValueError, match="Illegal transition"):
        machine.transition(RuntimePhase.BOOTSTRAPPED.value, "invalid downgrade")


def test_mark_repairing_from_healthy(bootstrapped_project: Path) -> None:
    machine = StateMachine(bootstrapped_project)

    result = machine.mark_repairing("verify failed")

    assert result["phase"] == RuntimePhase.REPAIRING.value
    assert machine.current() == RuntimePhase.REPAIRING.value
