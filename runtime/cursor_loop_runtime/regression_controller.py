"""Regression controller — schema and hash integrity with extensible levels."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import append_jsonl, sha256_file, utcnow


REQUIRED_CURSOR_FILES = [
    ".cursor/hooks.json",
]


class RegressionController:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)
        self.root = self.memory.paths.root

    def _baseline(self) -> dict[str, Any]:
        parts: list[str] = []
        hooks = self.root / ".cursor" / "hooks.json"
        if hooks.exists():
            parts.append(sha256_file(hooks))
        rules_dir = self.root / ".cursor" / "rules"
        if rules_dir.exists():
            for path in sorted(rules_dir.glob("*.mdc")):
                parts.append(sha256_file(path))
        combined = sha256_file(hooks) if hooks.exists() else "0" * 64
        if parts:
            from .models import sha256_text

            combined = sha256_text("|".join(parts))
        return {
            "baseline_artifact_id": "CURSOR_LOOP_BASELINE",
            "baseline_version": "1.0.0",
            "baseline_hash": combined,
            "candidate_artifact_id": "CURSOR_LOOP_CANDIDATE",
            "candidate_version": "1.0.0",
            "candidate_hash": combined,
        }

    def check_l1_schema(self) -> list[str]:
        failures: list[str] = []
        hooks = self.root / ".cursor" / "hooks.json"
        if not hooks.exists():
            failures.append("L1 missing .cursor/hooks.json")
        else:
            try:
                data = json.loads(hooks.read_text(encoding="utf-8"))
                if data.get("version") != 1:
                    failures.append("L1 hooks.json version must be 1")
                if "hooks" not in data or not isinstance(data["hooks"], dict):
                    failures.append("L1 hooks.json missing hooks object")
            except json.JSONDecodeError as exc:
                failures.append(f"L1 hooks.json invalid JSON: {exc}")

        for rel in REQUIRED_CURSOR_FILES:
            if not (self.root / rel).exists():
                failures.append(f"L1 missing {rel}")

        state = self.memory.paths.state
        if state.exists():
            try:
                json.loads(state.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"L1 invalid state JSON: {exc}")
        return failures

    def check_l2_hash(self) -> list[str]:
        failures: list[str] = []
        manifest = self.memory.paths.manifest
        if not manifest.exists():
            return failures
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for entry in data.get("files", []):
            rel = entry.get("path")
            expected = entry.get("sha256")
            if not rel or not expected:
                continue
            path = self.root / rel
            if not path.exists():
                failures.append(f"L2 missing: {rel}")
                continue
            actual = sha256_file(path)
            if actual != expected:
                failures.append(f"L2 hash mismatch: {rel}")
        return failures

    def run(self) -> dict[str, Any]:
        self.memory.ensure()
        started = time.perf_counter()
        l1 = self.check_l1_schema()
        l2 = self.check_l2_hash()
        failures = l1 + l2
        result = "PASS" if not failures else "FAIL"
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        record = {
            "regression_id": f"REG-{utcnow()}",
            "result": result,
            "failure_count": len(failures),
            "failures": failures,
            "levels": {
                "L1_SCHEMA": "PASS" if not l1 else "FAIL",
                "L2_HASH": "PASS" if not l2 else "FAIL",
                "L3_PROVENANCE": "NOT_RUN",
                "L4_SEMANTIC": "NOT_RUN",
                "L5_TEMPORAL": "NOT_RUN",
                "L6_DEPENDENCY": "NOT_RUN",
                "L7_REPRESENTATIVE": "NOT_RUN",
                "L8_BOOT": "NOT_RUN",
            },
            **self._baseline(),
            "elapsed_ms": round(elapsed_ms, 3),
            "timestamp": utcnow(),
        }
        append_jsonl(self.memory.paths.regression_history, record)
        self.memory.record_timing("regress", elapsed_ms, result == "PASS")
        self.memory.log_event("REGRESSION_RUN", "NOTICE" if result == "PASS" else "ERROR", result)
        from .loop_controller import LoopController

        LoopController(self.root).mark_gate_result(
            "REGRESSION",
            result == "PASS",
            failures=failures,
            section_id="REGRESSION",
        )
        return record
