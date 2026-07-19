"""Loop controller — failed-section loop with localize, repair, and stop dispositions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import Disposition, LoopState, read_json, sha256_text, utcnow, write_json_atomic


class LoopController:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)
        self.root = self.memory.paths.root

    def fingerprint_failure(self, gate: str | None, failures: list[str]) -> str:
        payload = json.dumps({"gate": gate, "failures": sorted(failures)}, sort_keys=True)
        return sha256_text(payload)[:16]

    def localize(self, failures: list[str]) -> dict[str, Any]:
        """Map failure strings to repair sections."""
        sections: dict[str, list[str]] = {}
        for item in failures:
            upper = item.upper()
            if item.startswith("L") or "REGRESSION" in upper or "HASH" in upper:
                section = "REGRESSION"
            elif "HOOK" in upper:
                section = "HOOKS"
            elif "SKILL" in upper:
                section = "SKILLS"
            elif "AGENT" in upper:
                section = "AGENTS"
            elif "RULE" in upper:
                section = "RULES"
            elif "EVIDENCE" in upper or "CONFIDENCE" in upper:
                section = "EVIDENCE"
            elif "MEMORY" in upper or "STATE" in upper or "BOOT" in upper:
                section = "RUNTIME"
            else:
                section = "VERIFY"
            sections.setdefault(section, []).append(item)
        primary = next(iter(sections), "VERIFY")
        return {"primary_section": primary, "sections": sections}

    def attempt_repair(self, section: str) -> dict[str, Any]:
        """Apply deterministic repairs for a localized section."""
        actions: list[str] = []
        cursor = self.root / ".cursor"
        cursor.mkdir(parents=True, exist_ok=True)

        if section in {"RUNTIME", "VERIFY", "EVIDENCE"}:
            self.memory.ensure()
            actions.append("ensured runtime memory")

        if section in {"HOOKS", "VERIFY"}:
            hooks = cursor / "hooks.json"
            if not hooks.exists():
                write_json_atomic(hooks, {"version": 1, "hooks": {}})
                actions.append("created .cursor/hooks.json")
            hooks_dir = cursor / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)
            actions.append("ensured .cursor/hooks/")

        if section in {"RULES", "SKILLS", "AGENTS", "VERIFY"}:
            for name in ("rules", "skills", "agents", "templates"):
                (cursor / name).mkdir(parents=True, exist_ok=True)
            actions.append("ensured cursor asset directories")

        if section == "REGRESSION":
            self.memory.ensure()
            actions.append("ensured regression prerequisites")

        self.memory.append_decision(
            "LOOP_REPAIR",
            "APPLIED" if actions else "NONE",
            f"Repair attempt for section {section}",
            section=section,
            actions=actions,
        )
        return {"section": section, "actions": actions, "result": "PASS" if actions else "NOOP"}

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

        performance = read_json(self.memory.paths.performance, {})
        performance["loop_iterations"] = int(performance.get("loop_iterations", 0)) + 1
        performance["updated_at"] = utcnow()
        write_json_atomic(self.memory.paths.performance, performance)

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
        verification = read_json(verify_path, {})
        result = verification.get("result")
        failures = list(verification.get("failures") or [])

        localization = self.localize(failures) if failures else {"primary_section": None, "sections": {}}
        repair: dict[str, Any] | None = None

        if result == "PASS":
            state = self.mark_gate_result("VERIFY", True)
        elif result == "FAIL":
            section = str(localization.get("primary_section") or "VERIFY")
            if self.memory.get_loop_state().disposition != Disposition.SAFE_STOP.value:
                repair = self.attempt_repair(section)
            state = self.mark_gate_result("VERIFY", False, failures=failures, section_id=section)
        else:
            state = self.memory.get_loop_state()
            state.disposition = Disposition.CONTINUE.value
            state.last_gate = "VERIFY"
            state.last_result = "UNKNOWN"
            self.memory.save_loop_state(state)

        return {
            "loop_state": state.to_dict(),
            "verification_result": result,
            "localization": localization,
            "repair": repair,
        }

    def status(self) -> dict[str, Any]:
        self.memory.ensure()
        return {
            "loop_state": self.memory.get_loop_state().to_dict(),
            "state": self.memory.get_state(),
            "performance": read_json(self.memory.paths.performance, {}),
        }
