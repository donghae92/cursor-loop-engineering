"""Tests for Cursor plugin packaging and local install."""

from __future__ import annotations

import json
from pathlib import Path

from cursor_loop_install.plugin import (
    doctor_plugin,
    install_plugin_local,
    remove_plugin_local,
    sync_plugin_layout,
    update_plugin_local,
    validate_plugin,
)
from cursor_loop.cli import main


def test_sync_and_validate_plugin(framework_root: Path) -> None:
    sync = sync_plugin_layout(framework_root)
    assert sync["result"] == "PASS"
    result = validate_plugin(framework_root)
    assert result["result"] == "PASS", result.get("failures")
    assert result["counts"]["rules"] >= 12
    assert result["counts"]["skills"] >= 14
    assert result["counts"]["agents"] >= 10
    assert result["counts"]["commands"] >= 6
    assert result["counts"]["hooks"] >= 7
    assert (framework_root / ".cursor-plugin" / "plugin.json").exists()
    assert (framework_root / ".cursor" / "rules").exists()
    assert (framework_root / "mcp.json").exists()


def test_plugin_doctor_repair(tmp_path: Path, monkeypatch) -> None:
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    (plugin / ".cursor-plugin").mkdir()
    (plugin / ".cursor-plugin" / "plugin.json").write_text(
        json.dumps({"name": "cursor-loop-engineering", "version": "2.0.0", "description": "test"}),
        encoding="utf-8",
    )
    (plugin / "VERSION").write_text("2.0.0\n", encoding="utf-8")
    cursor = plugin / ".cursor"
    (cursor / "rules").mkdir(parents=True)
    (cursor / "rules" / "architecture.mdc").write_text(
        "---\ndescription: x\nalwaysApply: true\n---\n# A\n",
        encoding="utf-8",
    )
    (cursor / "skills" / "validation").mkdir(parents=True)
    (cursor / "skills" / "validation" / "SKILL.md").write_text(
        "---\nname: validation\ndescription: d\n---\n# V\n",
        encoding="utf-8",
    )
    (cursor / "agents").mkdir(parents=True)
    (cursor / "agents" / "ceo.md").write_text("---\nname: ceo\ndescription: d\n---\n# C\n", encoding="utf-8")
    (cursor / "hooks").mkdir(parents=True)
    (cursor / "hooks" / "pre_task.py").write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
    (cursor / "hooks.json").write_text(
        json.dumps({"version": 1, "hooks": {"preToolUse": [{"command": ".cursor/hooks/pre_task.py"}]}}),
        encoding="utf-8",
    )

    monkeypatch.setattr("cursor_loop_install.plugin.framework_root", lambda: plugin)
    result = doctor_plugin(plugin, repair=True)
    assert (plugin / "mcp.json").exists()
    assert (plugin / ".cursor" / "commands").exists()
    assert result["repairs"]


def test_plugin_install_update_remove(framework_root: Path, tmp_path: Path, monkeypatch) -> None:
    local = tmp_path / "local-plugins"
    monkeypatch.setattr("cursor_loop_install.plugin.local_plugins_dir", lambda: local)
    sync_plugin_layout(framework_root)
    installed = install_plugin_local(framework_root, force=True)
    assert installed["result"] == "PASS", installed
    dest = local / "cursor-loop-engineering"
    assert dest.exists()
    assert (dest / ".cursor-plugin" / "plugin.json").exists()
    assert (dest / "rules").exists()
    assert (dest / "commands").exists()

    updated = update_plugin_local(framework_root)
    assert updated["result"] == "PASS"
    assert Path(updated["backup"]).exists()

    removed = remove_plugin_local()
    assert removed["result"] == "PASS"
    assert not dest.exists()


def test_cli_plugin_validate(capsys, framework_root: Path) -> None:
    rc = main(["plugin-validate", "--self"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["result"] == "PASS"
