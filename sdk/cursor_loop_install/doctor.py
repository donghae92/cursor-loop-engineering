"""Doctor — diagnose and repair missing files, broken refs, invalid metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from cursor_loop_runtime.memory_controller import MemoryController
from cursor_loop_runtime.models import read_json, sha256_file, utcnow, write_json_atomic
from cursor_loop_runtime.scheduler import Scheduler
from cursor_loop_runtime.state_machine import StateMachine

from .merger import install_assets
from .versions import framework_root, read_framework_version
from .verify import REQUIRED_AGENTS, REQUIRED_HOOKS, REQUIRED_RULES, REQUIRED_SKILLS


def doctor(root: Path, *, repair: bool = False) -> dict[str, Any]:
    root = root.resolve()
    issues: list[str] = []
    repairs: list[str] = []
    py = sys.version_info
    if py < (3, 9):
        issues.append(f"Python 3.9+ required; found {py.major}.{py.minor}")

    if not (root / ".cursor").exists():
        issues.append(".cursor directory missing — run: cle install .")
    if not (root / ".cursor-loop").exists():
        issues.append(".cursor-loop missing — run: cle bootstrap")

    hooks = root / ".cursor" / "hooks.json"
    if hooks.exists():
        try:
            data = json.loads(hooks.read_text(encoding="utf-8"))
            if data.get("version") != 1:
                issues.append("hooks.json version must be 1")
        except json.JSONDecodeError:
            issues.append("hooks.json is not valid JSON")

    for script in (root / ".cursor" / "hooks").glob("*.py") if (root / ".cursor" / "hooks").exists() else []:
        if not script.stat().st_mode & 0o111:
            issues.append(f"hook not executable: {script.name}")
            if repair:
                script.chmod(script.stat().st_mode | 0o111)
                repairs.append(f"chmod +x {script.name}")

    manifest_path = root / ".cursor-loop" / "install_manifest.json"
    framework_installed = manifest_path.exists()

    # Missing managed assets only matter if the framework was previously installed
    missing_assets: list[str] = []
    if framework_installed:
        for name in REQUIRED_RULES:
            if not (root / ".cursor" / "rules" / f"{name}.mdc").exists():
                missing_assets.append(f"rules/{name}.mdc")
        for name in REQUIRED_SKILLS:
            if not (root / ".cursor" / "skills" / name / "SKILL.md").exists():
                missing_assets.append(f"skills/{name}/SKILL.md")
        for name in REQUIRED_AGENTS:
            if not (root / ".cursor" / "agents" / f"{name}.md").exists():
                missing_assets.append(f"agents/{name}.md")
        for name in REQUIRED_HOOKS:
            if not (root / ".cursor" / "hooks" / name).exists():
                missing_assets.append(f"hooks/{name}")
        if missing_assets:
            issues.append(f"missing managed assets: {len(missing_assets)}")
            if repair:
                merge = install_assets(root, force=False, preserve_custom=True)
                repairs.append(
                    "restored assets "
                    f"written={len(merge.get('written', []))} updated={len(merge.get('updated', []))}"
                )

    if framework_installed:
        manifest = read_json(manifest_path, {})
        broken = []
        for entry in manifest.get("files", []):
            rel = entry.get("path")
            if not rel:
                continue
            path = root / rel
            if not path.exists():
                broken.append(rel)
            elif entry.get("sha256") and sha256_file(path) != entry["sha256"]:
                issues.append(f"hash drift: {rel}")
        if broken:
            issues.append(f"broken manifest refs: {len(broken)}")
            if repair:
                files = []
                for entry in manifest.get("files", []):
                    rel = entry.get("path")
                    path = root / rel if rel else None
                    if path and path.exists():
                        files.append({"path": rel, "sha256": sha256_file(path), "managed": True})
                manifest["files"] = files
                manifest["framework_version"] = read_framework_version()
                manifest["repaired_at"] = utcnow()
                write_json_atomic(manifest_path, manifest)
                repairs.append("rebuilt install_manifest.json")

    if repair:
        memory = MemoryController(root)
        memory.ensure()
        Scheduler(root).run()
        StateMachine(root).mark_healthy("doctor repair")
        repairs.append("runtime memory ensured")
        remaining: list[str] = []
        if py < (3, 9):
            remaining.append(f"Python 3.9+ required; found {py.major}.{py.minor}")
        if not (root / ".cursor").exists():
            remaining.append(".cursor directory missing — run: cle install .")
        if not (root / ".cursor-loop").exists():
            remaining.append(".cursor-loop missing — run: cle bootstrap")
        if not (root / ".cursor" / "hooks.json").exists():
            remaining.append("hooks.json still missing")
        if (root / ".cursor-loop" / "install_manifest.json").exists():
            for name in REQUIRED_RULES:
                if not (root / ".cursor" / "rules" / f"{name}.mdc").exists():
                    remaining.append(f"still missing rule: {name}")
                    break
        issues = remaining

    result = "PASS" if not issues else "FAIL"
    if repair and repairs and not issues:
        result = "PASS"

    return {
        "result": result,
        "issues": issues,
        "repairs": repairs,
        "python": f"{py.major}.{py.minor}.{py.micro}",
        "framework_root": str(framework_root()),
        "framework_version": read_framework_version(),
        "project_root": str(root),
        "checked_at": utcnow(),
    }
