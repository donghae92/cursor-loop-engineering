"""Checkpoint manager — durable snapshots of runtime memory."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import sha256_file, utcnow, write_json_atomic


class CheckpointManager:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)

    def create(self, label: str = "manual") -> dict[str, Any]:
        self.memory.ensure()
        checkpoint_id = f"CP-{utcnow().replace(':', '').replace('+', '-')}-{label}"
        dest = self.memory.paths.checkpoints / checkpoint_id
        dest.mkdir(parents=True, exist_ok=True)
        copied: list[str] = []
        for name in (
            "state.json",
            "loop_state.json",
            "performance.json",
            "task_queue.jsonl",
            "backlog.jsonl",
            "regression_history.jsonl",
            "decision_history.jsonl",
            "evidence_log.jsonl",
            "events.jsonl",
            "install_manifest.json",
            "last_verify.json",
        ):
            src = self.memory.paths.runtime_dir / name
            if src.exists():
                shutil.copy2(src, dest / name)
                copied.append(name)
        meta = {
            "checkpoint_id": checkpoint_id,
            "label": label,
            "created_at": utcnow(),
            "files": copied,
        }
        write_json_atomic(dest / "checkpoint.json", meta)
        self.memory.log_event("CHECKPOINT_CREATE", "NOTICE", checkpoint_id)
        return meta

    def list_checkpoints(self) -> list[dict[str, Any]]:
        self.memory.ensure()
        rows: list[dict[str, Any]] = []
        for path in sorted(self.memory.paths.checkpoints.glob("*/checkpoint.json")):
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        return rows

    def restore(self, checkpoint_id: str) -> dict[str, Any]:
        self.memory.ensure()
        src = self.memory.paths.checkpoints / checkpoint_id
        if not src.exists():
            raise FileNotFoundError(f"checkpoint not found: {checkpoint_id}")
        restored: list[str] = []
        for path in src.iterdir():
            if path.name == "checkpoint.json":
                continue
            target = self.memory.paths.runtime_dir / path.name
            shutil.copy2(path, target)
            restored.append(path.name)
        self.memory.log_event("CHECKPOINT_RESTORE", "NOTICE", checkpoint_id, files=restored)
        return {"result": "PASS", "checkpoint_id": checkpoint_id, "restored": restored}

    def verify_checkpoint(self, checkpoint_id: str) -> dict[str, Any]:
        src = self.memory.paths.checkpoints / checkpoint_id / "checkpoint.json"
        if not src.exists():
            return {"result": "FAIL", "reason": "missing checkpoint metadata"}
        meta = json.loads(src.read_text(encoding="utf-8"))
        missing = []
        for name in meta.get("files", []):
            if not (self.memory.paths.checkpoints / checkpoint_id / name).exists():
                missing.append(name)
        return {
            "result": "PASS" if not missing else "FAIL",
            "checkpoint_id": checkpoint_id,
            "missing": missing,
            "meta_hash": sha256_file(src),
        }
