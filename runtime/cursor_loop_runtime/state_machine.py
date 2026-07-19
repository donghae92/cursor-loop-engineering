"""State machine for framework health and phase transitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import RuntimePhase


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    RuntimePhase.UNINITIALIZED.value: {RuntimePhase.BOOTSTRAPPED.value},
    RuntimePhase.BOOTSTRAPPED.value: {
        RuntimePhase.HEALTHY.value,
        RuntimePhase.DEGRADED.value,
        RuntimePhase.BLOCKED.value,
    },
    RuntimePhase.HEALTHY.value: {
        RuntimePhase.DEGRADED.value,
        RuntimePhase.BLOCKED.value,
        RuntimePhase.REPAIRING.value,
        RuntimePhase.READY_FOR_RELEASE.value,
    },
    RuntimePhase.DEGRADED.value: {
        RuntimePhase.HEALTHY.value,
        RuntimePhase.BLOCKED.value,
        RuntimePhase.REPAIRING.value,
    },
    RuntimePhase.BLOCKED.value: {
        RuntimePhase.REPAIRING.value,
        RuntimePhase.HEALTHY.value,
    },
    RuntimePhase.REPAIRING.value: {
        RuntimePhase.HEALTHY.value,
        RuntimePhase.DEGRADED.value,
        RuntimePhase.BLOCKED.value,
    },
    RuntimePhase.READY_FOR_RELEASE.value: {
        RuntimePhase.HEALTHY.value,
        RuntimePhase.DEGRADED.value,
    },
}


class StateMachine:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)

    def current(self) -> str:
        state = self.memory.get_state()
        return str(state.get("phase") or RuntimePhase.UNINITIALIZED.value)

    def can_transition(self, target: str) -> bool:
        current = self.current()
        if current == target:
            return True
        return target in ALLOWED_TRANSITIONS.get(current, set())

    def transition(self, target: str, reason: str) -> dict[str, Any]:
        current = self.current()
        if current != target and target not in ALLOWED_TRANSITIONS.get(current, set()):
            raise ValueError(f"Illegal transition {current} -> {target}")
        updated = self.memory.update_state(phase=target, last_transition_reason=reason)
        self.memory.log_event(
            "STATE_TRANSITION",
            "NOTICE",
            f"{current} -> {target}",
            reason=reason,
        )
        self.memory.append_decision("STATE_TRANSITION", "OK", reason, from_phase=current, to_phase=target)
        return updated

    def mark_healthy(self, reason: str = "verification passed") -> dict[str, Any]:
        current = self.current()
        if current == RuntimePhase.UNINITIALIZED.value:
            self.transition(RuntimePhase.BOOTSTRAPPED.value, "bootstrap")
        if self.current() == RuntimePhase.BOOTSTRAPPED.value:
            return self.transition(RuntimePhase.HEALTHY.value, reason)
        if self.current() in {
            RuntimePhase.DEGRADED.value,
            RuntimePhase.BLOCKED.value,
            RuntimePhase.REPAIRING.value,
            RuntimePhase.READY_FOR_RELEASE.value,
        }:
            return self.transition(RuntimePhase.HEALTHY.value, reason)
        return self.memory.update_state(health="HEALTHY")

    def mark_repairing(self, reason: str) -> dict[str, Any]:
        current = self.current()
        if current == RuntimePhase.HEALTHY.value or current == RuntimePhase.DEGRADED.value or current == RuntimePhase.BLOCKED.value:
            return self.transition(RuntimePhase.REPAIRING.value, reason)
        if current == RuntimePhase.BOOTSTRAPPED.value:
            self.transition(RuntimePhase.DEGRADED.value, reason)
            return self.transition(RuntimePhase.REPAIRING.value, reason)
        return self.memory.update_state(health="REPAIRING", last_transition_reason=reason)
