"""Cursor plugin packaging — `.cursor/` is canonical; local install materializes plugin layout."""

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
CURSOR_COMPONENT_DIRS = ("rules", "skills", "agents", "commands", "hooks", "templates")


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


def sync_plugin_layout(root: Path | None = None) -> dict[str, Any]:
    """Ensure plugin manifest points at `.cursor/` components (canonical source)."""
    root = plugin_root(root)
    cursor = root / ".cursor"
    checked: list[str] = []
    for name in CURSOR_COMPONENT_DIRS:
        path = cursor / name
        if path.exists():
            checked.append(name)

    manifest_file = root / ".cursor-plugin" / "plugin.json"
    if manifest_file.exists():
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        data["rules"] = "./.cursor/rules/"
        data["skills"] = "./.cursor/skills/"
        data["agents"] = "./.cursor/agents/"
        data["commands"] = "./.cursor/commands/"
        data["hooks"] = "./.cursor/hooks.json"
        data["mcpServers"] = "./mcp.json"
        write_json_atomic(manifest_file, data)
        checked.append("plugin.json")

    mcp = root / "mcp.json"
    if not mcp.exists():
        write_json_atomic(mcp, {"mcpServers": {}})
        checked.append("mcp.json")

    return {"result": "PASS", "checked": checked, "synced_at": utcnow(), "canonical": ".cursor"}


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
    checks["manifest"] = "PASS" if not failures else "FAIL"

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

    # Support source layout (.cursor/*) and materialized marketplace layout (root rules/skills/...).
    cursor = root / ".cursor"
    materialized = (root / "rules").exists() or (root / "skills").exists()
    if materialized:
        rules_dir = root / "rules"
        skills_dir = root / "skills"
        agents_dir = root / "agents"
        commands_dir = root / "commands"
        hooks_dir = root / "hooks"
        hooks_json = root / "hooks" / "hooks.json"
        layout = "materialized"
    else:
        rules_dir = cursor / "rules"
        skills_dir = cursor / "skills"
        agents_dir = cursor / "agents"
        commands_dir = cursor / "commands"
        hooks_dir = cursor / "hooks"
        hooks_json = cursor / "hooks.json"
        layout = "source"

    counts = {
        "rules": len(list(rules_dir.glob("*.mdc"))) if rules_dir.exists() else 0,
        "skills": len(list(skills_dir.glob("*/SKILL.md"))) if skills_dir.exists() else 0,
        "agents": len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0,
        "commands": len(list(commands_dir.glob("*.md"))) if commands_dir.exists() else 0,
        "hooks": len([p for p in hooks_dir.glob("*.py") if p.name != "_common.py"]) if hooks_dir.exists() else 0,
    }
    # Include helper modules in hook inventory but do not require them for the minimum.
    if hooks_dir.exists():
        counts["hooks"] = len(list(hooks_dir.glob("*.py")))

    for key, minimum in (("rules", 1), ("skills", 1), ("agents", 1), ("commands", 1), ("hooks", 1)):
        if counts[key] < minimum:
            failures.append(f"insufficient {key}: {counts[key]} < {minimum}")
            checks[key] = "FAIL"
        else:
            checks[key] = "PASS"

    if not hooks_json.exists():
        failures.append("missing hooks.json" if materialized else "missing .cursor/hooks.json")
        checks["hooks_json"] = "FAIL"
    else:
        checks["hooks_json"] = "PASS"
    checks["layout"] = layout

    if not (root / "mcp.json").exists():
        failures.append("missing mcp.json")
        checks["mcp"] = "FAIL"
    else:
        checks["mcp"] = "PASS"

    logo = str(manifest.get("logo") or "")
    if logo:
        logo_path = root / logo
        if not logo_path.exists():
            failures.append(f"logo missing: {logo}")
            checks["logo"] = "FAIL"
        else:
            checks["logo"] = "PASS"
    else:
        checks["logo"] = "ABSENT"

    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "checks": checks,
        "counts": counts,
        "manifest": {"name": manifest.get("name"), "version": manifest.get("version"), "displayName": manifest.get("displayName")},
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
        cursor = root / ".cursor"
        cursor.mkdir(parents=True, exist_ok=True)
        for name in CURSOR_COMPONENT_DIRS:
            (cursor / name).mkdir(parents=True, exist_ok=True)
            repairs.append(f"ensured .cursor/{name}")
        mcp = root / "mcp.json"
        if not mcp.exists():
            write_json_atomic(mcp, {"mcpServers": {}})
            repairs.append("created mcp.json")
        commands = cursor / "commands"
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
                    "rules": "./.cursor/rules/",
                    "skills": "./.cursor/skills/",
                    "agents": "./.cursor/agents/",
                    "commands": "./.cursor/commands/",
                    "hooks": "./.cursor/hooks.json",
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
    """Copy canonical `.cursor/` components into Cursor plugin-root layout at dest."""
    copied: list[str] = []
    cursor = root / ".cursor"
    mapping = {
        "rules": "rules",
        "skills": "skills",
        "agents": "agents",
        "commands": "commands",
        "hooks": "hooks",
        "templates": "templates",
    }
    for src_name, dest_name in mapping.items():
        src = cursor / src_name
        if not src.exists():
            continue
        target = dest / dest_name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target)
        copied.append(dest_name)

    hooks_json = cursor / "hooks.json"
    if hooks_json.exists():
        data = json.loads(hooks_json.read_text(encoding="utf-8"))
        plugin_hooks = {"version": data.get("version", 1), "hooks": {}}
        for event, entries in (data.get("hooks") or {}).items():
            rewritten = []
            for entry in entries or []:
                item = dict(entry)
                command = str(item.get("command") or "")
                if command:
                    item["command"] = "./hooks/" + Path(command).name
                rewritten.append(item)
            plugin_hooks["hooks"][event] = rewritten
        (dest / "hooks").mkdir(parents=True, exist_ok=True)
        write_json_atomic(dest / "hooks" / "hooks.json", plugin_hooks)
        copied.append("hooks/hooks.json")

    # Manifest for installed plugin uses root-relative component paths
    src_manifest = root / ".cursor-plugin" / "plugin.json"
    (dest / ".cursor-plugin").mkdir(parents=True, exist_ok=True)
    if src_manifest.exists():
        data = json.loads(src_manifest.read_text(encoding="utf-8"))
    else:
        data = {"name": PLUGIN_NAME, "description": "Cursor Loop Engineering"}
    data["rules"] = "./rules/"
    data["skills"] = "./skills/"
    data["agents"] = "./agents/"
    data["commands"] = "./commands/"
    data["hooks"] = "./hooks/hooks.json"
    data["mcpServers"] = "./mcp.json"
    data["logo"] = "assets/logo.svg"
    data["version"] = data.get("version") or read_framework_version(root)
    write_json_atomic(dest / ".cursor-plugin" / "plugin.json", data)
    copied.append(".cursor-plugin")

    for rel in ("mcp.json", "VERSION", "COMPATIBILITY.json", "LICENSE", "README.md", "MARKETPLACE.md", "CHANGELOG.md", "SECURITY.md"):
        src = root / rel
        if src.exists():
            shutil.copy2(src, dest / rel)
            copied.append(rel)

    assets = root / "assets"
    if assets.exists():
        target = dest / "assets"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(assets, target)
        copied.append("assets")

    docs = root / "docs"
    if docs.exists():
        target = dest / "docs"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(docs, target, ignore=shutil.ignore_patterns("__pycache__"))
        copied.append("docs")

    examples = root / "examples"
    if examples.exists():
        target = dest / "examples"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(examples, target)
        copied.append("examples")

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
