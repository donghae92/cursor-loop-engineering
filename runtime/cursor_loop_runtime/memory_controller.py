"""Memory controller — durable runtime memory and event logging."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import (
    LoopState,
    WorkspacePaths,
    append_jsonl,
    read_json,
    read_jsonl,
    utcnow,
    write_json_atomic,
)


class MemoryController:
    def __init__(self, root: Path | None = None) -> None:
        self.paths = WorkspacePaths(Path(root or Path.cwd()).resolve())

    def ensure(self) -> dict[str, str]:
        runtime = self.paths.runtime_dir
        runtime.mkdir(parents=True, exist_ok=True)
        self.paths.checkpoints.mkdir(parents=True, exist_ok=True)
        self.paths.quarantine.mkdir(parents=True, exist_ok=True)

        if not self.paths.loop_state.exists():
            write_json_atomic(self.paths.loop_state, LoopState().to_dict())
        if not self.paths.state.exists():
            write_json_atomic(
                self.paths.state,
                {
                    "framework": "cursor-loop-engineering",
                    "version": "1.0.0",
                    "phase": "BOOTSTRAPPED",
                    "health": "HEALTHY",
                    "updated_at": utcnow(),
                },
            )
        if not self.paths.performance.exists():
            write_json_atomic(
                self.paths.performance,
                {
                    "validate_runs": 0,
                    "validate_pass": 0,
                    "validate_fail": 0,
                    "regress_runs": 0,
                    "regress_pass": 0,
                    "regress_fail": 0,
                    "loop_iterations": 0,
                    "schedule_runs": 0,
                    "avg_validate_ms": 0.0,
                    "avg_regress_ms": 0.0,
                    "updated_at": utcnow(),
                },
            )
        for path in (
            self.paths.task_queue,
            self.paths.backlog,
            self.paths.regression_history,
            self.paths.decision_history,
            self.paths.evidence_log,
            self.paths.events,
        ):
            if not path.exists():
                path.write_text("", encoding="utf-8")
        return {
            "runtime_dir": str(self.paths.runtime_dir),
            "state": str(self.paths.state),
            "loop_state": str(self.paths.loop_state),
        }

    def log_event(self, event_type: str, severity: str, message: str, **extra: Any) -> dict[str, Any]:
        self.ensure()
        event = {
            "event_id": f"EVT-{utcnow()}",
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "timestamp": utcnow(),
            **extra,
        }
        append_jsonl(self.paths.events, event)
        return event

    def append_decision(self, decision_type: str, result: str, rationale: str, **extra: Any) -> dict[str, Any]:
        self.ensure()
        record = {
            "decision_id": f"DEC-{utcnow()}",
            "decision_type": decision_type,
            "result": result,
            "rationale": rationale,
            "timestamp": utcnow(),
            **extra,
        }
        append_jsonl(self.paths.decision_history, record)
        return record

    def record_timing(self, kind: str, elapsed_ms: float, passed: bool) -> dict[str, Any]:
        self.ensure()
        perf = read_json(self.paths.performance, {})
        runs_key = f"{kind}_runs"
        pass_key = f"{kind}_pass"
        fail_key = f"{kind}_fail"
        avg_key = f"avg_{kind}_ms"
        runs = int(perf.get(runs_key, 0)) + 1
        prev_avg = float(perf.get(avg_key, 0.0))
        perf[runs_key] = runs
        perf[pass_key] = int(perf.get(pass_key, 0)) + (1 if passed else 0)
        perf[fail_key] = int(perf.get(fail_key, 0)) + (0 if passed else 1)
        perf[avg_key] = ((prev_avg * (runs - 1)) + elapsed_ms) / runs
        perf["updated_at"] = utcnow()
        write_json_atomic(self.paths.performance, perf)
        return perf

    def update_state(self, **updates: Any) -> dict[str, Any]:
        self.ensure()
        state = read_json(self.paths.state, {})
        state.update(updates)
        state["updated_at"] = utcnow()
        write_json_atomic(self.paths.state, state)
        return state

    def get_state(self) -> dict[str, Any]:
        self.ensure()
        return read_json(self.paths.state, {})

    def get_loop_state(self) -> LoopState:
        self.ensure()
        return LoopState.from_dict(read_json(self.paths.loop_state, {}))

    def save_loop_state(self, loop_state: LoopState) -> LoopState:
        loop_state.updated_at = utcnow()
        write_json_atomic(self.paths.loop_state, loop_state.to_dict())
        return loop_state

    def recent_events(self, limit: int = 20) -> list[dict[str, Any]]:
        self.ensure()
        rows = read_jsonl(self.paths.events)
        return rows[-limit:]
