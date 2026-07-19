"""Cursor plugin packaging, validation, local install, and update."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from cursor_loop_runtime.models import sha256_file, utcnow, write_json_atomic

from .versions import framework_root, read_framework_version

PLUGIN_NAME = "cursor-loop-engineering"
NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")

REQUIRED_MANIFEST_FIELDS = ("name", "version", "description")
COMPONENT_DIRS = ("rules", "skills", "agents", "commands", "hooks", "templates", "examples")


def plugin_root(root: Path | None = None) -> Path:
    return (root or framework_root()).resolve()


def manifest_path(root: Path | None = None) -> Path:
    return plugin_root(root) / ".cursor-plugin" / "plugin.json"


def local_plugins_dir() -> Path:
    return Path.home() / ".cursor" / "plugins" / "local"


def load_manifest(root: Path | None = None) -> dict[str, Any]:
    path = manifest_path(root)
    if not path.exists():
        raise FileNotFoundError(f"plugin manifest missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _merge_tree(source: Path, dest: Path) -> None:
    """Copy source into dest, preserving files that only exist on dest."""
    dest.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        rel = path.relative_to(source)
        target = dest / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def sync_plugin_layout(root: Path | None = None) -> dict[str, Any]:
    """Sync `.cursor/` assets into plugin-root component directories."""
    root = plugin_root(root)
    src = root / ".cursor"
    copied: list[str] = []
    for name in ("rules", "skills", "agents", "templates", "examples"):
        source = src / name
        dest = root / name
        if not source.exists():
            continue
        # Merge both ways so plugin-root-only and .cursor-only assets survive.
        if dest.exists():
            _merge_tree(dest, source)
        _merge_tree(source, dest)
        copied.append(name)

    # Commands: keep plugin-root commands authoritative; mirror into .cursor/commands
    commands_root = root / "commands"
    commands_cursor = src / "commands"
    if commands_root.exists():
        commands_cursor.mkdir(parents=True, exist_ok=True)
        for path in commands_root.glob("*.md"):
            shutil.copy2(path, commands_cursor / path.name)
            copied.append(f"commands/{path.name}")
    elif commands_cursor.exists():
        shutil.copytree(commands_cursor, commands_root)
        copied.append("commands")

    hooks_src = src / "hooks"
    hooks_dest = root / "hooks"
    hooks_dest.mkdir(parents=True, exist_ok=True)
    if hooks_src.exists():
        for script in hooks_src.glob("*.py"):
            target = hooks_dest / script.name
            shutil.copy2(script, target)
            target.chmod(target.stat().st_mode | 0o111)
            copied.append(f"hooks/{script.name}")

    hooks_json_src = src / "hooks.json"
    if hooks_json_src.exists():
        data = json.loads(hooks_json_src.read_text(encoding="utf-8"))
        plugin_hooks = {"version": data.get("version", 1), "hooks": {}}
        for event, entries in (data.get("hooks") or {}).items():
            rewritten = []
            for entry in entries or []:
                item = dict(entry)
                command = str(item.get("command") or "")
                if command.startswith(".cursor/hooks/"):
                    item["command"] = "./hooks/" + Path(command).name
                rewritten.append(item)
            plugin_hooks["hooks"][event] = rewritten
        write_json_atomic(hooks_dest / "hooks.json", plugin_hooks)
        copied.append("hooks/hooks.json")

    return {"result": "PASS", "copied": copied, "synced_at": utcnow()}


def validate_plugin(root: Path | None = None) -> dict[str, Any]:
    root = plugin_root(root)
    failures: list[str] = []
    checks: dict[str, str] = {}

    path = manifest_path(root)
    if not path.exists():
        return {
            "result": "FAIL",
            "failure_count": 1,
            "failures": ["missing .cursor-plugin/plugin.json"],
            "checks": {"manifest": "FAIL"},
            "validated_at": utcnow(),
        }

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "result": "FAIL",
            "failure_count": 1,
            "failures": [f"invalid plugin.json: {exc}"],
            "checks": {"manifest": "FAIL"},
            "validated_at": utcnow(),
        }

    for field in REQUIRED_MANIFEST_FIELDS:
        if not manifest.get(field):
            failures.append(f"manifest missing {field}")
    name = str(manifest.get("name") or "")
    if name and not NAME_PATTERN.match(name):
        failures.append(f"invalid plugin name: {name}")
    checks["manifest"] = "PASS" if not any(f.startswith("manifest") or f.startswith("invalid plugin") for f in failures) else "FAIL"

    # Component presence
    for rel in (
        "rules",
        "skills",
        "agents",
        "commands",
        "hooks/hooks.json",
        "mcp.json",
        "assets/logo.svg",
    ):
        if not (root / rel).exists():
            failures.append(f"missing component path: {rel}")
    checks["components"] = "PASS" if not any(f.startswith("missing component") for f in failures) else "FAIL"

    # Count inventories
    counts = {
        "rules": len(list((root / "rules").glob("*.mdc"))) if (root / "rules").exists() else 0,
        "skills": len(list((root / "skills").glob("*/SKILL.md"))) if (root / "skills").exists() else 0,
        "agents": len(list((root / "agents").glob("*.md"))) if (root / "agents").exists() else 0,
        "commands": len(list((root / "commands").glob("*.md"))) if (root / "commands").exists() else 0,
        "hooks": len(list((root / "hooks").glob("*.py"))) if (root / "hooks").exists() else 0,
    }
    if counts["rules"] < 1:
        failures.append("no rules discovered")
    if counts["skills"] < 1:
        failures.append("no skills discovered")
    if counts["agents"] < 1:
        failures.append("no agents discovered")
    if counts["commands"] < 1:
        failures.append("no commands discovered")
    if counts["hooks"] < 1:
        failures.append("no hook scripts discovered")
    checks["inventory"] = "PASS" if not any(
        f.startswith("no ") for f in failures
    ) else "FAIL"

    # hooks.json integrity
    hooks_json = root / "hooks" / "hooks.json"
    if hooks_json.exists():
        try:
            hooks = json.loads(hooks_json.read_text(encoding="utf-8"))
            if hooks.get("version") != 1:
                failures.append("hooks/hooks.json version must be 1")
            for event, entries in (hooks.get("hooks") or {}).items():
                for entry in entries or []:
                    command = str(entry.get("command") or "")
                    if command.startswith("./hooks/"):
                        script = root / command[2:]
                        if not script.exists():
                            failures.append(f"hook command missing: {command}")
        except json.JSONDecodeError as exc:
            failures.append(f"hooks/hooks.json invalid: {exc}")
    checks["hooks"] = "PASS" if not any("hook" in f for f in failures) else "FAIL"

    # mcp.json
    mcp = root / "mcp.json"
    if mcp.exists():
        try:
            data = json.loads(mcp.read_text(encoding="utf-8"))
            if "mcpServers" not in data:
                failures.append("mcp.json missing mcpServers")
            checks["mcp"] = "PASS" if "mcpServers" in data else "FAIL"
        except json.JSONDecodeError as exc:
            failures.append(f"mcp.json invalid: {exc}")
            checks["mcp"] = "FAIL"
    else:
        checks["mcp"] = "FAIL"
        failures.append("missing mcp.json")

    # Version consistency
    version_file = root / "VERSION"
    file_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else None
    manifest_version = str(manifest.get("version") or "")
    if file_version and manifest_version and file_version != manifest_version:
        failures.append(f"version mismatch VERSION={file_version} plugin.json={manifest_version}")
        checks["version"] = "FAIL"
    else:
        checks["version"] = "PASS"

    result = {
        "result": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "checks": checks,
        "counts": counts,
        "manifest": {
            "name": manifest.get("name"),
            "version": manifest.get("version"),
            "displayName": manifest.get("displayName"),
        },
        "validated_at": utcnow(),
        "root": str(root),
    }
    write_json_atomic(root / ".cursor-loop" / "last_plugin_validate.json", result)
    return result


def doctor_plugin(root: Path | None = None, *, repair: bool = False) -> dict[str, Any]:
    root = plugin_root(root)
    issues: list[str] = []
    repairs: list[str] = []
    validation = validate_plugin(root)
    if validation["result"] != "PASS":
        issues.extend(validation.get("failures") or [])
        if repair:
            sync = sync_plugin_layout(root)
            repairs.append(f"synced components: {len(sync.get('copied') or [])}")
            # ensure mcp.json
            mcp = root / "mcp.json"
            if not mcp.exists():
                write_json_atomic(mcp, {"mcpServers": {}})
                repairs.append("created mcp.json")
            # ensure commands dir has at least install command
            commands = root / "commands"
            commands.mkdir(parents=True, exist_ok=True)
            if not any(commands.glob("*.md")):
                (commands / "cle-verify.md").write_text(
                    "---\nname: cle-verify\ndescription: Verify installation\n---\n\n# Verify\n\n```bash\ncle verify\n```\n",
                    encoding="utf-8",
                )
                repairs.append("seeded cle-verify command")
            validation = validate_plugin(root)
            issues = list(validation.get("failures") or [])

    result = "PASS" if not issues else "FAIL"
    return {
        "result": result,
        "issues": issues,
        "repairs": repairs,
        "validation": validation,
        "checked_at": utcnow(),
    }


def install_plugin_local(
    root: Path | None = None,
    *,
    force: bool = False,
    plugins_dir: Path | None = None,
) -> dict[str, Any]:
    """Install this plugin into ~/.cursor/plugins/local/<name> for Cursor /add-plugin discovery."""
    root = plugin_root(root)
    sync_plugin_layout(root)
    validation = validate_plugin(root)
    if validation["result"] != "PASS":
        return {"result": "FAIL", "error": "plugin validation failed", "validation": validation}

    manifest = load_manifest(root)
    name = str(manifest.get("name") or PLUGIN_NAME)
    base = Path(plugins_dir).resolve() if plugins_dir else local_plugins_dir()
    dest = base / name
    base.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if not force:
            # incremental update path
            return update_plugin_local(root, plugins_dir=base)
        shutil.rmtree(dest)

    include = [
        ".cursor-plugin",
        "rules",
        "skills",
        "agents",
        "commands",
        "hooks",
        "templates",
        "examples",
        "assets",
        "mcp.json",
        "VERSION",
        "COMPATIBILITY.json",
        "LICENSE",
        "README.md",
        "MARKETPLACE.md",
        "docs",
    ]
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for rel in include:
        src = root / rel
        if not src.exists():
            continue
        target = dest / rel
        if src.is_dir():
            shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        copied.append(rel)

    meta = {
        "framework": PLUGIN_NAME,
        "plugin_name": name,
        "version": manifest.get("version"),
        "installed_at": utcnow(),
        "source": str(root),
        "destination": str(dest),
        "files": [{"path": rel, "sha256": sha256_file(dest / rel) if (dest / rel).is_file() else None} for rel in copied],
    }
    write_json_atomic(dest / "plugin.install.json", meta)
    # Also record in framework runtime if present
    runtime = root / ".cursor-loop"
    if runtime.exists():
        write_json_atomic(runtime / "plugin_install.json", meta)

    return {
        "result": "PASS",
        "plugin_name": name,
        "version": manifest.get("version"),
        "destination": str(dest),
        "copied": copied,
        "validation": validation,
        "hint": "Open Cursor → Plugins / Marketplace, or use local plugins under ~/.cursor/plugins/local/",
    }


def update_plugin_local(root: Path | None = None, *, plugins_dir: Path | None = None) -> dict[str, Any]:
    root = plugin_root(root)
    sync_plugin_layout(root)
    validation = validate_plugin(root)
    if validation["result"] != "PASS":
        return {"result": "FAIL", "error": "plugin validation failed", "validation": validation}
    manifest = load_manifest(root)
    name = str(manifest.get("name") or PLUGIN_NAME)
    base = Path(plugins_dir).resolve() if plugins_dir else local_plugins_dir()
    dest = base / name
    if not dest.exists():
        return install_plugin_local(root, force=True, plugins_dir=base)

    # Backup existing local plugin
    backup = base / f".backup-{name}-{utcnow().replace(':', '').replace('+', '-')}"
    if dest.exists():
        shutil.copytree(dest, backup)

    # Refresh managed component trees
    for rel in ("rules", "skills", "agents", "commands", "hooks", "templates", "examples", "assets", ".cursor-plugin"):
        src = root / rel
        target = dest / rel
        if not src.exists():
            continue
        if target.exists():
            shutil.rmtree(target) if target.is_dir() else target.unlink()
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
    for rel in ("mcp.json", "VERSION", "COMPATIBILITY.json", "LICENSE", "README.md", "MARKETPLACE.md"):
        src = root / rel
        if src.exists():
            shutil.copy2(src, dest / rel)

    meta = {
        "framework": PLUGIN_NAME,
        "plugin_name": name,
        "version": manifest.get("version") or read_framework_version(root),
        "updated_at": utcnow(),
        "source": str(root),
        "destination": str(dest),
        "backup": str(backup),
    }
    write_json_atomic(dest / "plugin.install.json", meta)
    return {"result": "PASS", "updated": True, "destination": str(dest), "backup": str(backup), "validation": validation}


def remove_plugin_local(*, plugins_dir: Path | None = None) -> dict[str, Any]:
    base = Path(plugins_dir).resolve() if plugins_dir else local_plugins_dir()
    dest = base / PLUGIN_NAME
    if not dest.exists():
        return {"result": "PASS", "removed": False, "reason": "not installed"}
    shutil.rmtree(dest)
    return {"result": "PASS", "removed": True, "destination": str(dest), "removed_at": utcnow()}
