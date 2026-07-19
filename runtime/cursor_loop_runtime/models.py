"""Shared models and path helpers for Cursor Loop Engineering runtime."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp.replace(path)


class Disposition(str, Enum):
    IDLE = "IDLE"
    CONTINUE = "CONTINUE"
    SAFE_STOP = "SAFE_STOP"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class TaskStatus(str, Enum):
    BACKLOG = "BACKLOG"
    WAITING = "WAITING"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
    FAILED = "FAILED"


class RuntimePhase(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    BOOTSTRAPPED = "BOOTSTRAPPED"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    REPAIRING = "REPAIRING"
    READY_FOR_RELEASE = "READY_FOR_RELEASE"


@dataclass
class WorkspacePaths:
    root: Path

    @property
    def cursor(self) -> Path:
        return self.root / ".cursor"

    @property
    def rules(self) -> Path:
        return self.cursor / "rules"

    @property
    def skills(self) -> Path:
        return self.cursor / "skills"

    @property
    def agents(self) -> Path:
        return self.cursor / "agents"

    @property
    def hooks(self) -> Path:
        return self.cursor / "hooks"

    @property
    def hooks_json(self) -> Path:
        return self.cursor / "hooks.json"

    @property
    def runtime_dir(self) -> Path:
        return self.root / ".cursor-loop"

    @property
    def state(self) -> Path:
        return self.runtime_dir / "state.json"

    @property
    def loop_state(self) -> Path:
        return self.runtime_dir / "loop_state.json"

    @property
    def task_queue(self) -> Path:
        return self.runtime_dir / "task_queue.jsonl"

    @property
    def backlog(self) -> Path:
        return self.runtime_dir / "backlog.jsonl"

    @property
    def regression_history(self) -> Path:
        return self.runtime_dir / "regression_history.jsonl"

    @property
    def decision_history(self) -> Path:
        return self.runtime_dir / "decision_history.jsonl"

    @property
    def evidence_log(self) -> Path:
        return self.runtime_dir / "evidence_log.jsonl"

    @property
    def performance(self) -> Path:
        return self.runtime_dir / "performance.json"

    @property
    def events(self) -> Path:
        return self.runtime_dir / "events.jsonl"

    @property
    def checkpoints(self) -> Path:
        return self.runtime_dir / "checkpoints"

    @property
    def quarantine(self) -> Path:
        return self.runtime_dir / "quarantine"

    @property
    def manifest(self) -> Path:
        return self.runtime_dir / "install_manifest.json"


@dataclass
class LoopState:
    loop_id: str = "LOOP-V1"
    iteration: int = 0
    section_id: str | None = None
    retry_budget: int = 5
    retries_used: int = 0
    last_gate: str | None = None
    last_result: str | None = None
    disposition: str = Disposition.IDLE.value
    last_failure_fingerprint: str | None = None
    identical_failure_count: int = 0
    updated_at: str = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoopState":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Task:
    task_id: str
    mission: str
    status: str = TaskStatus.READY.value
    worker_role: str = "developer"
    dependencies: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    blocker: str | None = None
    created_at: str = field(default_factory=utcnow)
    updated_at: str = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})
