"""Installer, migration, rollback, and export/import integration tests."""

from __future__ import annotations

import json
import tarfile
from pathlib import Path

import pytest

from cursor_loop_install.detector import detect_project
from cursor_loop_install.framework_core import install_into, remove_framework, rollback, update
from cursor_loop_install.export_import import export_package, import_package
from cursor_loop_install.migration_engine import run_upgrade
from cursor_loop_install.verify import verify_framework
from cursor_loop.cli import main


def test_install_into_empty_project(tmp_path: Path, framework_root: Path) -> None:
    target = tmp_path / "empty"
    target.mkdir()
    result = install_into(target)
    assert result["result"] == "PASS"
    assert (target / ".cursor" / "hooks.json").exists()
    assert (target / ".cursor-loop" / "install_manifest.json").exists()
    assert verify_framework(target)["result"] == "PASS"


def test_install_merges_existing_hooks_without_losing_custom(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    cursor = target / ".cursor"
    cursor.mkdir()
    (cursor / "hooks").mkdir()
    custom_hook = cursor / "hooks" / "custom_user.py"
    custom_hook.write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
    (cursor / "hooks.json").write_text(
        json.dumps(
            {
                "version": 1,
                "hooks": {
                    "sessionStart": [{"command": ".cursor/hooks/custom_user.py"}],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    # custom rule that must survive
    rules = cursor / "rules"
    rules.mkdir()
    custom_rule = rules / "my-team.mdc"
    custom_rule.write_text("---\ndescription: team\nalwaysApply: true\n---\n# Team\n", encoding="utf-8")

    result = install_into(target)
    assert result["result"] == "PASS"
    assert custom_rule.exists()
    assert custom_hook.exists()
    hooks = json.loads((cursor / "hooks.json").read_text(encoding="utf-8"))
    assert "sessionStart" in hooks["hooks"]
    assert "preToolUse" in hooks["hooks"]


def test_update_backs_up_before_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    install_into(target)
    managed = target / ".cursor" / "rules" / "architecture.mdc"
    original = managed.read_text(encoding="utf-8")
    managed.write_text(original + "\n# local edit\n", encoding="utf-8")
    result = update(target, force=True)
    assert result["result"] == "PASS"
    backups = list((target / ".cursor-loop" / "backups").glob("*/backup.json"))
    assert backups, "expected a backup before overwrite"


def test_migration_upgrade_and_rollback(tmp_path: Path) -> None:
    target = tmp_path / "migrate"
    target.mkdir()
    install_into(target)
    manifest = target / ".cursor-loop" / "install_manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["framework_version"] = "1.0.0"
    data["version"] = "1.0.0"
    data["installed_version"] = "1.0.0"
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    upgraded = run_upgrade(target, "1.1.0")
    assert upgraded["result"] == "PASS"
    assert "v1_0_0__v1_1_0" in upgraded["applied"]
    assert (target / ".cursor-loop" / "versions.json").exists()

    rolled = rollback(target)
    assert rolled["result"] == "PASS"
    assert rolled["installed_version"] == "1.0.0"


def test_export_and_import_roundtrip(tmp_path: Path) -> None:
    exported = export_package(tmp_path / "dist")
    assert exported["result"] == "PASS"
    archive = Path(exported["archive"])
    assert archive.exists()
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert any(name.endswith("VERSION") for name in names)

    target = tmp_path / "from_release"
    target.mkdir()
    imported = import_package(archive, target)
    assert imported["result"] == "PASS"
    assert verify_framework(target)["result"] == "PASS"


def test_remove_keeps_custom_and_can_purge_runtime(tmp_path: Path) -> None:
    target = tmp_path / "remove-me"
    target.mkdir()
    install_into(target)
    custom = target / ".cursor" / "rules" / "keep-me.mdc"
    custom.write_text("---\ndescription: keep\nalwaysApply: false\n---\n# Keep\n", encoding="utf-8")
    removed = remove_framework(target, keep_custom=True, purge_runtime=False)
    assert removed["result"] == "PASS"
    assert custom.exists()
    assert not (target / ".cursor" / "rules" / "architecture.mdc").exists()

    install_into(target)
    purged = remove_framework(target, keep_custom=True, purge_runtime=True)
    assert purged["result"] == "PASS"
    assert not (target / ".cursor-loop").exists()


def test_detect_monorepo_and_cli_doctor_repair(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "mono"
    (target / "packages").mkdir(parents=True)
    (target / "apps").mkdir()
    (target / "package.json").write_text("{}", encoding="utf-8")
    (target / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    kind = detect_project(target)["repository_kind"]
    assert kind == "monorepo"

    install_into(target)
    # break an asset then repair
    (target / ".cursor" / "rules" / "architecture.mdc").unlink()
    rc = main(["doctor", "--path", str(target), "--repair"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["result"] in {"PASS", "REPAIRED"}
    assert (target / ".cursor" / "rules" / "architecture.mdc").exists()
