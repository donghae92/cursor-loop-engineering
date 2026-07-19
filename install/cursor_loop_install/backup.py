"""Backup helpers for merge-safe installs."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from cursor_loop_runtime.models import utcnow, write_json_atomic


def backup_paths(target: Path, paths: list[Path], reason: str = "update") -> dict[str, Any]:
    stamp = utcnow().replace(":", "").replace("+", "-")
    backup_root = target / ".cursor-loop" / "backups" / f"{stamp}-{reason}"
    backup_root.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        try:
            rel = path.relative_to(target)
        except ValueError:
            rel = Path(path.name)
        dest = backup_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        copied.append(str(rel))
    meta = {
        "backup_id": backup_root.name,
        "reason": reason,
        "created_at": utcnow(),
        "files": copied,
        "path": str(backup_root),
    }
    write_json_atomic(backup_root / "backup.json", meta)
    return meta


def restore_backup(target: Path, backup_id: str) -> dict[str, Any]:
    backup_root = target / ".cursor-loop" / "backups" / backup_id
    if not backup_root.exists():
        raise FileNotFoundError(f"backup not found: {backup_id}")
    restored: list[str] = []
    for path in backup_root.rglob("*"):
        if not path.is_file() or path.name == "backup.json":
            continue
        rel = path.relative_to(backup_root)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        restored.append(str(rel))
    return {"result": "PASS", "backup_id": backup_id, "restored": restored}
