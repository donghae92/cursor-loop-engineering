#!/usr/bin/env python3
"""Install Cursor Loop Engineering into a target project."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRAMEWORK_ROOT / "runtime"))
sys.path.insert(0, str(FRAMEWORK_ROOT / "sdk"))

from cursor_loop_runtime.models import sha256_file, utcnow, write_json_atomic  # noqa: E402
from cursor_loop_runtime.memory_controller import MemoryController  # noqa: E402
from cursor_loop_runtime.state_machine import StateMachine  # noqa: E402


ASSET_DIRS = (
    "rules",
    "skills",
    "agents",
    "hooks",
    "templates",
    "examples",
)


def install_into(target: Path, force: bool = False) -> dict:
    target = target.resolve()
    if not target.exists() or not target.is_dir():
        raise FileNotFoundError(f"target project not found: {target}")

    cursor_src = FRAMEWORK_ROOT / ".cursor"
    cursor_dest = target / ".cursor"
    same_tree = cursor_src.resolve() == cursor_dest.resolve()

    files: list[dict] = []

    def track(rel: str, path: Path) -> None:
        if path.exists() and path.is_file():
            files.append({"path": rel, "sha256": sha256_file(path)})

    if same_tree:
        # Installing into the framework repository itself — hash existing assets only.
        hooks_json = cursor_dest / "hooks.json"
        track(".cursor/hooks.json", hooks_json)
        for name in ASSET_DIRS:
            src = cursor_dest / name
            if not src.exists():
                continue
            for path in src.rglob("*"):
                if path.is_file():
                    rel = f".cursor/{name}/{path.relative_to(src).as_posix()}"
                    track(rel, path)
    else:
        hooks_json_src = cursor_src / "hooks.json"
        if hooks_json_src.exists():
            cursor_dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(hooks_json_src, cursor_dest / "hooks.json")
            track(".cursor/hooks.json", cursor_dest / "hooks.json")

        for name in ASSET_DIRS:
            src = cursor_src / name
            dest = cursor_dest / name
            if not src.exists():
                continue
            for path in src.rglob("*"):
                if path.is_dir():
                    continue
                rel_inside = path.relative_to(src)
                target_file = dest / rel_inside
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if force or not target_file.exists():
                    shutil.copy2(path, target_file)
                rel = f".cursor/{name}/{rel_inside.as_posix()}"
                track(rel, target_file)

    # Make hook scripts executable
    hooks_dir = cursor_dest / "hooks"
    if hooks_dir.exists():
        for script in hooks_dir.glob("*.py"):
            script.chmod(script.stat().st_mode | 0o111)

    memory = MemoryController(target)
    created = memory.ensure()
    StateMachine(target).mark_healthy("framework installed")

    manifest = {
        "framework": "cursor-loop-engineering",
        "version": "1.0.0",
        "installed_at": utcnow(),
        "source": str(FRAMEWORK_ROOT),
        "target": str(target),
        "files": files,
        "self_install": same_tree,
    }
    write_json_atomic(memory.paths.manifest, manifest)
    memory.log_event("INSTALL", "NOTICE", f"Installed into {target}", file_count=len(files))

    # Write AGENTS.md snippet if missing
    agents_md = target / "AGENTS.md"
    if not agents_md.exists():
        agents_md.write_text(
            "# AGENTS.md\n\n"
            "This project uses **Cursor Loop Engineering**.\n\n"
            "## Quick commands\n\n"
            "```bash\n"
            "python3 -m cursor_loop status\n"
            "python3 -m cursor_loop verify\n"
            "python3 -m cursor_loop loop --once\n"
            "```\n\n"
            "Runtime memory lives in `.cursor-loop/`.\n"
            "Cursor assets live in `.cursor/`.\n",
            encoding="utf-8",
        )

    return {
        "result": "PASS",
        "target": str(target),
        "file_count": len(files),
        "runtime": created,
        "manifest": str(memory.paths.manifest),
        "self_install": same_tree,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install Cursor Loop Engineering into a project")
    parser.add_argument("target", nargs="?", default=".", help="Target project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing Cursor assets")
    args = parser.parse_args(argv)
    try:
        result = install_into(Path(args.target), force=args.force)
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result.get("result") == "PASS" else 4


if __name__ == "__main__":
    raise SystemExit(main())
