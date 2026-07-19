"""Loop controller — failed-section loop with retry budget and stop dispositions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import Disposition, LoopState, sha256_text


class LoopController:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)

    def fingerprint_failure(self, gate: str | None, failures: list[str]) -> str:
        payload = json.dumps({"gate": gate, "failures": sorted(failures)}, sort_keys=True)
        return sha256_text(payload)[:16]

    def mark_gate_result(
        self,
        gate: str,
        passed: bool,
        failures: list[str] | None = None,
        section_id: str | None = None,
    ) -> LoopState:
        self.memory.ensure()
        state = self.memory.get_loop_state()
        failures = failures or []
        state.iteration += 1
        state.section_id = section_id or state.section_id or gate
        state.last_gate = gate
        state.last_result = "PASS" if passed else "FAIL"

        perf = self.memory.paths.performance
        from .models import read_json, write_json_atomic, utcnow

        performance = read_json(perf, {})
        performance["loop_iterations"] = int(performance.get("loop_iterations", 0)) + 1
        performance["updated_at"] = utcnow()
        write_json_atomic(perf, performance)

        if passed:
            state.retries_used = 0
            state.identical_failure_count = 0
            state.last_failure_fingerprint = None
            state.disposition = Disposition.IDLE.value
            self.memory.save_loop_state(state)
            self.memory.append_decision("LOOP_GATE", "PASS", f"Gate {gate} passed", gate=gate)
            return state

        fingerprint = self.fingerprint_failure(gate, failures)
        if fingerprint == state.last_failure_fingerprint:
            state.identical_failure_count += 1
        else:
            state.identical_failure_count = 1
            state.last_failure_fingerprint = fingerprint
        state.retries_used += 1

        if state.identical_failure_count >= 3:
            state.disposition = Disposition.SAFE_STOP.value
            rationale = "Identical failure loop detected"
        elif state.retries_used > state.retry_budget:
            state.disposition = Disposition.MANUAL_REVIEW.value
            rationale = "Retry budget exhausted"
        else:
            state.disposition = Disposition.CONTINUE.value
            rationale = f"Gate {gate} failed; corrective loop continues"

        self.memory.save_loop_state(state)
        self.memory.append_decision("LOOP_GATE", state.disposition, rationale, gate=gate, failures=failures)
        self.memory.log_event("LOOP_GATE_RESULT", "ERROR", rationale, gate=gate)
        return state

    def run_once(self) -> dict[str, Any]:
        self.memory.ensure()
        verify_path = self.memory.paths.runtime_dir / "last_verify.json"
        from .models import read_json

        verification = read_json(verify_path, {})
        result = verification.get("result")
        failures = list(verification.get("failures") or [])
        if result == "PASS":
            state = self.mark_gate_result("VERIFY", True)
        elif result == "FAIL":
            state = self.mark_gate_result("VERIFY", False, failures=failures)
        else:
            state = self.memory.get_loop_state()
            state.disposition = Disposition.CONTINUE.value
            state.last_gate = "VERIFY"
            state.last_result = "UNKNOWN"
            self.memory.save_loop_state(state)
        return {"loop_state": state.to_dict(), "verification_result": result}

    def status(self) -> dict[str, Any]:
        self.memory.ensure()
        from .models import read_json

        return {
            "loop_state": self.memory.get_loop_state().to_dict(),
            "state": self.memory.get_state(),
            "performance": read_json(self.memory.paths.performance, {}),
        }
