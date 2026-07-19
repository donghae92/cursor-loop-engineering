"""Evidence controller — reject confidence-as-evidence; quarantine helpers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import append_jsonl, utcnow


class EvidenceController:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)

    def record(self, evidence_class: str, path: str, claim: str, **extra: Any) -> dict[str, Any]:
        self.memory.ensure()
        if evidence_class.upper() in {"CONFIDENCE", "MODEL_CONFIDENCE"}:
            raise ValueError("INSUFFICIENT_EVIDENCE: model confidence is not evidence")
        record = {
            "evidence_id": f"EVD-{utcnow()}",
            "evidence_class": evidence_class,
            "path": path,
            "claim": claim,
            "timestamp": utcnow(),
            **extra,
        }
        append_jsonl(self.memory.paths.evidence_log, record)
        return record

    def quarantine(self, path: Path, reason: str) -> dict[str, Any]:
        self.memory.ensure()
        src = path if path.is_absolute() else self.memory.paths.root / path
        if not src.exists():
            return {"result": "FAIL", "reason": f"missing: {src}"}
        dest = self.memory.paths.quarantine / src.name
        if dest.exists():
            dest = self.memory.paths.quarantine / f"{src.stem}-{utcnow().replace(':', '')}{src.suffix}"
        shutil.move(str(src), str(dest))
        self.memory.log_event("QUARANTINE", "WARNING", reason, path=str(dest))
        self.memory.append_decision("QUARANTINE", "MOVED", reason, path=str(dest))
        return {"result": "PASS", "quarantined_to": str(dest), "reason": reason}

    def check(self) -> dict[str, Any]:
        self.memory.ensure()
        required = [
            self.memory.paths.root / ".cursor" / "hooks.json",
            self.memory.paths.state,
        ]
        missing = [str(path.relative_to(self.memory.paths.root)) for path in required if not path.exists()]
        bad_confidence: list[str] = []
        from .models import read_jsonl

        for row in read_jsonl(self.memory.paths.evidence_log):
            if str(row.get("evidence_class", "")).upper() in {"CONFIDENCE", "MODEL_CONFIDENCE"}:
                bad_confidence.append(str(row.get("evidence_id")))
        result = "PASS" if not missing and not bad_confidence else "FAIL"
        out = {
            "result": result,
            "missing": missing,
            "confidence_violations": bad_confidence,
            "checked_at": utcnow(),
        }
        self.memory.log_event("EVIDENCE_CHECK", "NOTICE" if result == "PASS" else "ERROR", result)
        return out
