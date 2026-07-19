"""Upgrade 1.2.0 → 2.0.0: collapse dual layout; refresh managed .cursor assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cursor_loop_install.merger import install_assets
from cursor_loop_runtime.models import utcnow, write_json_atomic


def upgrade(target: Path, framework_root: Path | None = None) -> dict[str, Any]:
    target = Path(target).resolve()
    result = install_assets(target, force=True, source_root=Path(framework_root) if framework_root else None)
    # Remove obsolete dual-layout dirs if present in consumer projects (framework-managed only)
    removed = []
    for name in ("rules", "skills", "agents", "hooks", "commands", "templates"):
        # never delete .cursor/*; only accidental root duplicates from older plugin mirrors
        path = target / name
        marker = target / ".cursor-loop" / "install_manifest.json"
        if path.exists() and path.is_dir() and marker.exists() and not (target / "pyproject.toml").exists():
            # conservative: only note; do not delete consumer root dirs automatically
            removed.append(name)
    note = {
        "upgraded_to": "2.0.0",
        "canonical_assets": ".cursor/",
        "installer_package": "sdk/cursor_loop_install",
        "noted_root_duplicates": removed,
        "upgraded_at": utcnow(),
    }
    write_json_atomic(target / ".cursor-loop" / "upgrade_2_0_0.json", note)
    return {"result": "PASS", "install": result, "note": note}
