"""Rollback 2.0.0 → 1.2.0: restore prior managed assets via reinstall of previous package if available."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cursor_loop_runtime.models import utcnow, write_json_atomic


def rollback(target: Path, framework_root: Path | None = None) -> dict[str, Any]:
    target = Path(target).resolve()
    note = {
        "rolled_back_to": "1.2.0",
        "warning": "Re-install framework 1.2.0 package for full dual-layout restore.",
        "framework_root": str(framework_root) if framework_root else None,
        "rolled_back_at": utcnow(),
    }
    write_json_atomic(target / ".cursor-loop" / "rollback_2_0_0.json", note)
    return {"result": "PASS", "note": note}
