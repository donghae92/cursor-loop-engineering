"""Cursor plugin packaging — conventional root component dirs with `.cursor/` project mirror."""

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
PLUGIN_COMPONENT_DIRS = ("rules", "skills", "agents", "commands", "hooks", "templates")


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


def _copy_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _rewrite_hooks_json(data: dict[str, Any], *, plugin_style: bool) -> dict[str, Any]:
    out: dict[str, Any] = {"version": data.get("version", 1), "hooks": {}}
    for event, entries in (data.get("hooks") or {}).items():
        rewritten = []
        for entry in entries or []:
            item = dict(entry)
            command = str(item.get("command") or "")
            if command:
                name = Path(command).name
                item["command"] = f"./hooks/{name}" if plugin_style else f".cursor/hooks/{name}"
            rewritten.append(item)
        out["hooks"][event] = rewritten
    return out


def sync_plugin_layout(root: Path | None = None) -> dict[str, Any]:
    """Keep conventional root plugin dirs and `.cursor/` project mirror in sync.

    Canonical plugin source (Cursor convention): root `rules/`, `skills/`, `agents/`,
    `commands/`, `hooks/hooks.json`.

    Project-install mirror: `.cursor/` (used by the merge-safe installer).
    """
    root = plugin_root(root)
    cursor = root / ".cursor"
    copied: list[str] = []

    # Prefer existing root components; if missing, seed from .cursor once.
    for name in ("rules", "skills", "agents", "commands", "templates"):
        root_dir = root / name
        cursor_dir = cursor / name
        if not root_dir.exists() and cursor_dir.exists():
            _copy_tree(cursor_dir, root_dir)
            copied.append(f"seed-root:{name}")
        if root_dir.exists():
            cursor_dir.parent.mkdir(parents=True, exist_ok=True)
            _copy_tree(root_dir, cursor_dir)
            copied.append(f"mirror-cursor:{name}")

    # Hooks
    root_hooks = root / "hooks"
    cursor_hooks = cursor / "hooks"
    root_hooks.mkdir(parents=True, exist_ok=True)
    cursor_hooks.mkdir(parents=True, exist_ok=True)

    # Seed root hooks from .cursor if needed
    if not any(root_hooks.glob("*.py")) and cursor_hooks.exists():
        for script in cursor_hooks.glob("*.py"):
            target = root_hooks / script.name
            shutil.copy2(script, target)
            target.chmod(target.stat().st_mode | 0o111)
            copied.append(f"seed-root:hooks/{script.name}")

    # Mirror scripts both ways preferring root
    if any(root_hooks.glob("*.py")):
        for script in root_hooks.glob("*.py"):
            target = cursor_hooks / script.name
            shutil.copy2(script, target)
            target.chmod(target.stat().st_mode | 0o111)
            copied.append(f"mirror-cursor:hooks/{script.name}")

    # hooks.json: prefer root/hooks/hooks.json, else .cursor/hooks.json
    root_hooks_json = root_hooks / "hooks.json"
    cursor_hooks_json = cursor / "hooks.json"
    if root_hooks_json.exists():
        data = json.loads(root_hooks_json.read_text(encoding="utf-8"))
    elif cursor_hooks_json.exists():
        data = json.loads(cursor_hooks_json.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "hooks": {}}

    write_json_atomic(root_hooks_json, _rewrite_hooks_json(data, plugin_style=True))
    write_json_atomic(cursor_hooks_json, _rewrite_hooks_json(data, plugin_style=False))
    copied.append("hooks.json")

    manifest_file = root / ".cursor-plugin" / "plugin.json"
    if manifest_file.exists():
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        data["rules"] = "./rules/"
        data["skills"] = "./skills/"
        data["agents"] = "./agents/"
        data["commands"] = "./commands/"
        data["hooks"] = "./hooks/hooks.json"
        data["mcpServers"] = "./mcp.json"
        if (root / "assets" / "logo.svg").exists():
            data["logo"] = "assets/logo.svg"
        write_json_atomic(manifest_file, data)
        copied.append("plugin.json")

    mcp = root / "mcp.json"
    if not mcp.exists():
        write_json_atomic(mcp, {"mcpServers": {}})
        copied.append("mcp.json")

    return {
        "result": "PASS",
        "copied": copied,
        "synced_at": utcnow(),
        "canonical": "root-plugin-dirs",
        "project_mirror": ".cursor/",
    }


def validate_plugin(root: Path | None = None) -> dict[str, Any]:
    root = plugin_root(root)
    failures: list[str] = []
    checks: dict[str, str] = {}

    try:
        manifest = load_manifest(root)
    except FileNotFoundError as exc:
        return {
            "result": "FAIL",
            "failures": [str(exc)],
            "checks": {"manifest": "FAIL"},
            "counts": {},
            "validated_at": utcnow(),
            "root": str(root),
        }

    for field in REQUIRED_MANIFEST_FIELDS:
        if not manifest.get(field):
            failures.append(f"manifest missing {field}")
    name = str(manifest.get("name") or "")
    if name and not NAME_PATTERN.match(name):
        failures.append(f"invalid plugin name: {name}")
    checks["manifest"] = "PASS" if not any(
        item.startswith("manifest missing") or item.startswith("invalid plugin name") for item in failures
    ) else "FAIL"

    version_file = root / "VERSION"
    if version_file.exists():
        file_version = version_file.read_text(encoding="utf-8").strip()
        if str(manifest.get("version")) != file_version:
            failures.append(f"version mismatch manifest={manifest.get('version')} VERSION={file_version}")
            checks["version"] = "FAIL"
        else:
            checks["version"] = "PASS"
    else:
        failures.append("VERSION file missing")
        checks["version"] = "FAIL"

    # Conventional layout first; accept materialized/legacy `.cursor` as fallback.
    if (root / "rules").exists() or (root / "skills").exists():
        rules_dir = root / "rules"
        skills_dir = root / "skills"
        agents_dir = root / "agents"
        commands_dir = root / "commands"
        hooks_dir = root / "hooks"
        hooks_json = root / "hooks" / "hooks.json"
        layout = "convention"
    else:
        cursor = root / ".cursor"
        rules_dir = cursor / "rules"
        skills_dir = cursor / "skills"
        agents_dir = cursor / "agents"
        commands_dir = cursor / "commands"
        hooks_dir = cursor / "hooks"
        hooks_json = cursor / "hooks.json"
        layout = "legacy-cursor"

    counts = {
        "rules": len(list(rules_dir.glob("*.mdc"))) if rules_dir.exists() else 0,
        "skills": len(list(skills_dir.glob("*/SKILL.md"))) if skills_dir.exists() else 0,
        "agents": len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0,
        "commands": len(list(commands_dir.glob("*.md"))) if commands_dir.exists() else 0,
        "hooks": len(list(hooks_dir.glob("*.py"))) if hooks_dir.exists() else 0,
    }
    for key, minimum in (("rules", 1), ("skills", 1), ("agents", 1), ("commands", 1), ("hooks", 1)):
        if counts[key] < minimum:
            failures.append(f"insufficient {key}: {counts[key]} < {minimum}")
            checks[key] = "FAIL"
        else:
            checks[key] = "PASS"

    if not hooks_json.exists():
        failures.append("missing hooks/hooks.json" if layout == "convention" else "missing .cursor/hooks.json")
        checks["hooks_json"] = "FAIL"
    else:
        checks["hooks_json"] = "PASS"
        # Convention check: plugin-style commands use ./hooks/
        try:
            data = json.loads(hooks_json.read_text(encoding="utf-8"))
            if layout == "convention":
                for event, entries in (data.get("hooks") or {}).items():
                    for entry in entries or []:
                        command = str(entry.get("command") or "")
                        if command and not command.startswith("./hooks/"):
                            failures.append(f"non-conventional hook command under {event}: {command}")
                            checks["hooks_paths"] = "FAIL"
                checks.setdefault("hooks_paths", "PASS")
        except json.JSONDecodeError as exc:
            failures.append(f"hooks.json invalid: {exc}")
            checks["hooks_json"] = "FAIL"

    expected_paths = {
        "rules": "./rules/",
        "skills": "./skills/",
        "agents": "./agents/",
        "commands": "./commands/",
        "hooks": "./hooks/hooks.json",
        "mcpServers": "./mcp.json",
    }
    if layout == "convention":
        for key, expected in expected_paths.items():
            actual = str(manifest.get(key) or "")
            if actual and actual != expected:
                failures.append(f"manifest {key} should be {expected}, got {actual}")
                checks[f"manifest_{key}"] = "FAIL"
            else:
                checks[f"manifest_{key}"] = "PASS"

    if not (root / "mcp.json").exists():
        failures.append("missing mcp.json")
        checks["mcp"] = "FAIL"
    else:
        checks["mcp"] = "PASS"

    logo = str(manifest.get("logo") or "")
    if logo:
        if not (root / logo).exists():
            failures.append(f"logo missing: {logo}")
            checks["logo"] = "FAIL"
        else:
            checks["logo"] = "PASS"
    else:
        checks["logo"] = "ABSENT"

    checks["layout"] = layout
    return {
        "result": "PASS" if not failures else "FAIL",
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


def doctor_plugin(root: Path | None = None, *, repair: bool = False) -> dict[str, Any]:
    root = plugin_root(root)
    repairs: list[str] = []
    validation = validate_plugin(root)
    issues = list(validation.get("failures") or [])

    if repair and issues:
        sync = sync_plugin_layout(root)
        repairs.append(f"sync_plugin_layout:{sync.get('result')}")
        for name in PLUGIN_COMPONENT_DIRS:
            (root / name).mkdir(parents=True, exist_ok=True)
            repairs.append(f"ensured {name}/")
        if not (root / "mcp.json").exists():
            write_json_atomic(root / "mcp.json", {"mcpServers": {}})
            repairs.append("created mcp.json")
        commands = root / "commands"
        if not any(commands.glob("*.md")):
            (commands / "cle-verify.md").write_text(
                "---\nname: cle-verify\ndescription: Verify installation\n---\n\n# Verify\n\n```bash\ncle verify\n```\n",
                encoding="utf-8",
            )
            repairs.append("seeded cle-verify command")
        if not (root / ".cursor-plugin" / "plugin.json").exists():
            (root / ".cursor-plugin").mkdir(parents=True, exist_ok=True)
            write_json_atomic(
                root / ".cursor-plugin" / "plugin.json",
                {
                    "name": PLUGIN_NAME,
                    "version": read_framework_version(root),
                    "description": "Cursor Loop Engineering",
                    "rules": "./rules/",
                    "skills": "./skills/",
                    "agents": "./agents/",
                    "commands": "./commands/",
                    "hooks": "./hooks/hooks.json",
                    "mcpServers": "./mcp.json",
                },
            )
            repairs.append("created plugin manifest")
        validation = validate_plugin(root)
        issues = list(validation.get("failures") or [])

    return {
        "result": "PASS" if not issues else "FAIL",
        "issues": issues,
        "repairs": repairs,
        "validation": validation,
        "checked_at": utcnow(),
    }


def _materialize_plugin_tree(root: Path, dest: Path) -> list[str]:
    """Install conventional plugin tree into destination (already convention-shaped)."""
    copied: list[str] = []
    sync_plugin_layout(root)

    for rel in (
        ".cursor-plugin",
        "rules",
        "skills",
        "agents",
        "commands",
        "hooks",
        "templates",
        "assets",
        "mcp.json",
        "VERSION",
        "COMPATIBILITY.json",
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "SECURITY.md",
        "MARKETPLACE.md",
        "docs",
        "examples",
    ):
        src = root / rel
        if not src.exists():
            continue
        target = dest / rel
        if src.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        copied.append(rel)

    # Ensure installed manifest uses conventional paths
    manifest_file = dest / ".cursor-plugin" / "plugin.json"
    if manifest_file.exists():
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        data["rules"] = "./rules/"
        data["skills"] = "./skills/"
        data["agents"] = "./agents/"
        data["commands"] = "./commands/"
        data["hooks"] = "./hooks/hooks.json"
        data["mcpServers"] = "./mcp.json"
        if (dest / "assets" / "logo.svg").exists():
            data["logo"] = "assets/logo.svg"
        write_json_atomic(manifest_file, data)

    return copied


def install_plugin_local(
    root: Path | None = None,
    *,
    force: bool = False,
    plugins_dir: Path | None = None,
) -> dict[str, Any]:
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
            return update_plugin_local(root, plugins_dir=base)
        shutil.rmtree(dest)

    dest.mkdir(parents=True, exist_ok=True)
    copied = _materialize_plugin_tree(root, dest)
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
        "hint": "Enable under Cursor local plugins (~/.cursor/plugins/local/)",
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

    backup = base / f".backup-{name}-{utcnow().replace(':', '').replace('+', '-')}"
    shutil.copytree(dest, backup)
    shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    copied = _materialize_plugin_tree(root, dest)
    meta = {
        "framework": PLUGIN_NAME,
        "plugin_name": name,
        "version": manifest.get("version") or read_framework_version(root),
        "updated_at": utcnow(),
        "source": str(root),
        "destination": str(dest),
        "backup": str(backup),
        "copied": copied,
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
