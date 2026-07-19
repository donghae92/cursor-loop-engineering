"""Merge-safe asset installation — never overwrite without backup.

Canonical source of Cursor assets is `.cursor/` in the framework repository.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from cursor_loop_runtime.models import sha256_file

from .backup import backup_paths
from .versions import ASSET_DIRS, framework_root


def iter_framework_assets(source_root: Path | None = None) -> list[tuple[str, Path]]:
    """Yield (destination_relative_path, source_path) pairs from `.cursor/` only."""
    root = source_root or framework_root()
    cursor = root / ".cursor"
    assets: list[tuple[str, Path]] = []

    hooks_json = cursor / "hooks.json"
    if hooks_json.exists():
        assets.append((".cursor/hooks.json", hooks_json))

    for name in ASSET_DIRS:
        directory = cursor / name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                if name == "hooks" and path.name == "hooks.json":
                    continue
                rel = f".cursor/{name}/{path.relative_to(directory).as_posix()}"
                assets.append((rel, path))
    return assets


def merge_hooks_json(src: Path, dest: Path) -> dict[str, Any]:
    """Merge hook event lists; normalize commands to `.cursor/hooks/`."""
    src_data = json.loads(src.read_text(encoding="utf-8"))
    normalized_src: dict[str, Any] = {"version": src_data.get("version", 1), "hooks": {}}
    for event, entries in (src_data.get("hooks") or {}).items():
        rewritten = []
        for entry in entries or []:
            item = dict(entry)
            command = str(item.get("command") or "")
            name = Path(command).name
            if name.endswith(".py"):
                item["command"] = f".cursor/hooks/{name}"
            rewritten.append(item)
        normalized_src["hooks"][event] = rewritten

    if dest.exists():
        dest_data = json.loads(dest.read_text(encoding="utf-8"))
    else:
        dest_data = {"version": 1, "hooks": {}}
    merged_hooks = dict(dest_data.get("hooks") or {})
    added = 0
    for event, entries in (normalized_src.get("hooks") or {}).items():
        existing = list(merged_hooks.get(event) or [])
        existing_cmds = {(e.get("command"), e.get("matcher")) for e in existing if isinstance(e, dict)}
        for entry in entries or []:
            key = (entry.get("command"), entry.get("matcher"))
            if key not in existing_cmds:
                existing.append(entry)
                existing_cmds.add(key)
                added += 1
        merged_hooks[event] = existing
    out = {
        "version": normalized_src.get("version") or dest_data.get("version") or 1,
        "hooks": merged_hooks,
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return {"merged": True, "added_entries": added}


def install_assets(
    target: Path,
    *,
    force: bool = False,
    preserve_custom: bool = True,
    source_root: Path | None = None,
) -> dict[str, Any]:
    target = target.resolve()
    source_root = (source_root or framework_root()).resolve()
    same_tree = (source_root / ".cursor").resolve() == (target / ".cursor").resolve()

    written: list[str] = []
    skipped_custom: list[str] = []
    updated: list[str] = []
    backed_up: list[str] = []
    files_meta: list[dict[str, Any]] = []

    assets = iter_framework_assets(source_root)
    to_backup: list[Path] = []

    if same_tree:
        for rel, src in assets:
            dest = target / rel
            files_meta.append({"path": rel, "sha256": sha256_file(dest if dest.exists() else src), "managed": True})
            written.append(rel)
        return {
            "self_install": True,
            "written": written,
            "updated": [],
            "skipped_custom": [],
            "backed_up": [],
            "files": files_meta,
        }

    for rel, src in assets:
        dest = target / rel
        if dest.exists() and sha256_file(dest) != sha256_file(src):
            to_backup.append(dest)

    backup_meta = None
    if to_backup:
        reason = "force-update" if force else "merge"
        backup_meta = backup_paths(target, to_backup, reason=reason)
        backed_up = list(backup_meta.get("files") or [])

    _ = preserve_custom  # reserved: custom files outside asset set are never written here

    for rel, src in assets:
        dest = target / rel
        if rel == ".cursor/hooks.json":
            merge_hooks_json(src, dest)
            updated.append(rel)
            files_meta.append({"path": rel, "sha256": sha256_file(dest), "managed": True})
            continue

        if dest.exists():
            src_hash = sha256_file(src)
            dest_hash = sha256_file(dest)
            if src_hash == dest_hash:
                files_meta.append({"path": rel, "sha256": dest_hash, "managed": True})
                written.append(rel)
                continue
            shutil.copy2(src, dest)
            updated.append(rel)
            files_meta.append({"path": rel, "sha256": sha256_file(dest), "managed": True})
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            written.append(rel)
            files_meta.append({"path": rel, "sha256": sha256_file(dest), "managed": True})

    hooks_dir = target / ".cursor" / "hooks"
    if hooks_dir.exists():
        for script in hooks_dir.glob("*.py"):
            script.chmod(script.stat().st_mode | 0o111)

    return {
        "self_install": False,
        "written": written,
        "updated": updated,
        "skipped_custom": skipped_custom,
        "backed_up": backed_up,
        "backup": backup_meta,
        "files": files_meta,
    }
