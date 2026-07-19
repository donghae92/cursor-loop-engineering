"""Regression controller — L1–L8 integrity gates for Cursor Loop Engineering."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .memory_controller import MemoryController
from .models import append_jsonl, read_json, sha256_file, sha256_text, utcnow


REQUIRED_CURSOR_FILES = [
    ".cursor/hooks.json",
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _framework_version(root: Path) -> str:
    version_file = root / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    manifest = root / ".cursor-loop" / "install_manifest.json"
    if manifest.exists():
        data = read_json(manifest, {})
        return str(data.get("framework_version") or data.get("version") or "0.0.0")
    return "0.0.0"


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def _parse_iso(value: str) -> datetime | None:
    try:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


class RegressionController:
    def __init__(self, root: Path | None = None) -> None:
        self.memory = MemoryController(root)
        self.root = self.memory.paths.root

    def _baseline(self) -> dict[str, Any]:
        parts: list[str] = []
        hooks = self.root / ".cursor" / "hooks.json"
        if hooks.exists():
            parts.append(sha256_file(hooks))
        rules_dir = self.root / ".cursor" / "rules"
        if rules_dir.exists():
            for path in sorted(rules_dir.glob("*.mdc")):
                parts.append(sha256_file(path))
        combined = sha256_text("|".join(parts)) if parts else "0" * 64
        version = _framework_version(self.root)
        return {
            "baseline_artifact_id": "CURSOR_LOOP_BASELINE",
            "baseline_version": version,
            "baseline_hash": combined,
            "candidate_artifact_id": "CURSOR_LOOP_CANDIDATE",
            "candidate_version": version,
            "candidate_hash": combined,
        }

    def check_l1_schema(self) -> list[str]:
        failures: list[str] = []
        hooks = self.root / ".cursor" / "hooks.json"
        if not hooks.exists():
            failures.append("L1 missing .cursor/hooks.json")
        else:
            try:
                data = json.loads(hooks.read_text(encoding="utf-8"))
                if data.get("version") != 1:
                    failures.append("L1 hooks.json version must be 1")
                if "hooks" not in data or not isinstance(data["hooks"], dict):
                    failures.append("L1 hooks.json missing hooks object")
            except json.JSONDecodeError as exc:
                failures.append(f"L1 hooks.json invalid JSON: {exc}")

        for rel in REQUIRED_CURSOR_FILES:
            if not (self.root / rel).exists():
                failures.append(f"L1 missing {rel}")

        state = self.memory.paths.state
        if state.exists():
            try:
                json.loads(state.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"L1 invalid state JSON: {exc}")
        return failures

    def check_l2_hash(self) -> list[str]:
        failures: list[str] = []
        manifest = self.memory.paths.manifest
        if not manifest.exists():
            return failures
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for entry in data.get("files", []):
            rel = entry.get("path")
            expected = entry.get("sha256")
            if not rel or not expected:
                continue
            path = self.root / rel
            if not path.exists():
                failures.append(f"L2 missing: {rel}")
                continue
            actual = sha256_file(path)
            if actual != expected:
                failures.append(f"L2 hash mismatch: {rel}")
        return failures

    def check_l3_provenance(self) -> list[str]:
        """Install/manifest provenance when a managed install is claimed."""
        failures: list[str] = []
        manifest = self.memory.paths.manifest
        if not manifest.exists():
            return failures
        data = read_json(manifest, {})
        if not data.get("framework") and not data.get("framework_version"):
            failures.append("L3 install_manifest missing framework identity")
        files = data.get("files")
        if files is not None and not isinstance(files, list):
            failures.append("L3 install_manifest files must be a list")
        for entry in files or []:
            if not isinstance(entry, dict):
                failures.append("L3 install_manifest file entry must be object")
                continue
            if not entry.get("path"):
                failures.append("L3 install_manifest file entry missing path")
        return failures

    def check_l4_semantic(self) -> list[str]:
        """Frontmatter and naming invariants for Cursor assets."""
        failures: list[str] = []
        rules = self.root / ".cursor" / "rules"
        if rules.exists():
            for path in sorted(rules.glob("*.mdc")):
                meta = _parse_frontmatter(path.read_text(encoding="utf-8"))
                if "description" not in meta:
                    failures.append(f"L4 rule missing description frontmatter: {path.name}")
        skills = self.root / ".cursor" / "skills"
        if skills.exists():
            for skill_md in sorted(skills.glob("*/SKILL.md")):
                meta = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
                if "name" not in meta or "description" not in meta:
                    failures.append(f"L4 skill missing name/description: {skill_md.parent.name}")
        agents = self.root / ".cursor" / "agents"
        if agents.exists():
            for path in sorted(agents.glob("*.md")):
                meta = _parse_frontmatter(path.read_text(encoding="utf-8"))
                if "name" not in meta or "description" not in meta:
                    failures.append(f"L4 agent missing name/description: {path.name}")
        return failures

    def check_l5_temporal(self) -> list[str]:
        """Timestamps must be parseable and not in the far future."""
        failures: list[str] = []
        now = datetime.now(timezone.utc)
        state = read_json(self.memory.paths.state, {})
        updated = state.get("updated_at")
        if updated:
            parsed = _parse_iso(str(updated))
            if parsed is None:
                failures.append("L5 state.updated_at is not ISO-8601")
            else:
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                if parsed > now.replace(year=now.year + 1):
                    failures.append("L5 state.updated_at is unreasonably in the future")
        loop = read_json(self.memory.paths.loop_state, {})
        loop_updated = loop.get("updated_at")
        if loop_updated:
            parsed = _parse_iso(str(loop_updated))
            if parsed is None:
                failures.append("L5 loop_state.updated_at is not ISO-8601")
        return failures

    def check_l6_dependency(self) -> list[str]:
        """Hook commands and skill directories must resolve."""
        failures: list[str] = []
        hooks_path = self.root / ".cursor" / "hooks.json"
        if hooks_path.exists():
            data = json.loads(hooks_path.read_text(encoding="utf-8"))
            for event, entries in (data.get("hooks") or {}).items():
                for entry in entries or []:
                    command = str(entry.get("command") or "")
                    if not command:
                        failures.append(f"L6 empty hook command under {event}")
                        continue
                    script = self.root / command
                    if not script.exists():
                        # also accept basename under .cursor/hooks
                        alt = self.root / ".cursor" / "hooks" / Path(command).name
                        if not alt.exists():
                            failures.append(f"L6 missing hook script: {command}")
        skills = self.root / ".cursor" / "skills"
        if skills.exists():
            for directory in sorted(p for p in skills.iterdir() if p.is_dir()):
                if not (directory / "SKILL.md").exists():
                    failures.append(f"L6 skill directory missing SKILL.md: {directory.name}")
        return failures

    def check_l7_representative(self) -> list[str]:
        """Installed projects must carry a representative asset inventory."""
        failures: list[str] = []
        manifest = self.memory.paths.manifest
        if not manifest.exists():
            return failures
        rules = list((self.root / ".cursor" / "rules").glob("*.mdc")) if (self.root / ".cursor" / "rules").exists() else []
        skills = list((self.root / ".cursor" / "skills").glob("*/SKILL.md")) if (self.root / ".cursor" / "skills").exists() else []
        agents = list((self.root / ".cursor" / "agents").glob("*.md")) if (self.root / ".cursor" / "agents").exists() else []
        if not rules:
            failures.append("L7 installed project missing rules")
        if not skills:
            failures.append("L7 installed project missing skills")
        if not agents:
            failures.append("L7 installed project missing agents")
        if not (self.root / ".cursor" / "hooks.json").exists():
            failures.append("L7 installed project missing hooks.json")
        return failures

    def check_l8_boot(self) -> list[str]:
        """Runtime memory must boot and remain coherent."""
        failures: list[str] = []
        try:
            self.memory.ensure()
        except Exception as exc:  # noqa: BLE001 — surface boot failures
            return [f"L8 memory ensure failed: {exc}"]
        state = read_json(self.memory.paths.state, {})
        if not state.get("framework"):
            failures.append("L8 state missing framework")
        health = str(state.get("health") or "")
        if health and health not in {"HEALTHY", "DEGRADED", "BOOTSTRAPPED", "UNKNOWN", "REPAIRING"}:
            failures.append(f"L8 unexpected health value: {health}")
        if not self.memory.paths.loop_state.exists():
            failures.append("L8 missing loop_state.json")
        return failures

    def run(self) -> dict[str, Any]:
        self.memory.ensure()
        started = time.perf_counter()
        levels = {
            "L1_SCHEMA": self.check_l1_schema(),
            "L2_HASH": self.check_l2_hash(),
            "L3_PROVENANCE": self.check_l3_provenance(),
            "L4_SEMANTIC": self.check_l4_semantic(),
            "L5_TEMPORAL": self.check_l5_temporal(),
            "L6_DEPENDENCY": self.check_l6_dependency(),
            "L7_REPRESENTATIVE": self.check_l7_representative(),
            "L8_BOOT": self.check_l8_boot(),
        }
        failures: list[str] = []
        level_results: dict[str, str] = {}
        for name, items in levels.items():
            failures.extend(items)
            level_results[name] = "PASS" if not items else "FAIL"
        result = "PASS" if not failures else "FAIL"
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        record = {
            "regression_id": f"REG-{utcnow()}",
            "result": result,
            "failure_count": len(failures),
            "failures": failures,
            "levels": level_results,
            **self._baseline(),
            "elapsed_ms": round(elapsed_ms, 3),
            "timestamp": utcnow(),
        }
        append_jsonl(self.memory.paths.regression_history, record)
        self.memory.record_timing("regress", elapsed_ms, result == "PASS")
        self.memory.log_event("REGRESSION_RUN", "NOTICE" if result == "PASS" else "ERROR", result)
        from .loop_controller import LoopController

        LoopController(self.root).mark_gate_result(
            "REGRESSION",
            result == "PASS",
            failures=failures,
            section_id="REGRESSION",
        )
        return record
