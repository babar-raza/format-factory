"""
test_capability_parity.py — Governance Tests for TC-CAP-015

Three independent tests that read source registries DIRECTLY (no toolchain dependency).
Defense-in-depth: if tools/capability_sync/ has a bug, these tests still catch broken pointers.

Registered in skill-registry.yaml as test_paths for validate-capability-parity.
"""
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SKILL_REG = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
_CMD_REG = REPO_ROOT / ".claude" / "commands" / "command-registry.yaml"
_ROUTING_REG = REPO_ROOT / ".supervisor" / "capability-routing-registry.yaml"
_CMD_DIR = REPO_ROOT / ".claude" / "commands"
_EXCLUDED_STEMS = {"_readme", "command-registry"}


def _load_skill_registry() -> dict:
    return yaml.safe_load(_SKILL_REG.read_text(encoding="utf-8", errors="replace")) or {}


def _load_command_registry() -> dict:
    return yaml.safe_load(_CMD_REG.read_text(encoding="utf-8", errors="replace")) or {}


def _load_routing_registry() -> dict:
    return yaml.safe_load(_ROUTING_REG.read_text(encoding="utf-8", errors="replace")) or {}


def test_all_active_skills_have_command_files():
    """Every active skill must have its command_file present on disk."""
    data = _load_skill_registry()
    skills = data.get("skills", [])
    failures = []
    for skill in skills:
        if skill.get("status") == "deprecated":
            continue
        skill_id = skill.get("skill_id", "<unknown>")
        cmd_file = skill.get("command_file")
        if not cmd_file:
            failures.append(f"{skill_id}: missing command_file field")
            continue
        full_path = REPO_ROOT / cmd_file
        if not full_path.exists():
            failures.append(f"{skill_id}: command_file not on disk: {cmd_file}")
    assert not failures, (
        f"Active skills with missing command files ({len(failures)}):\n"
        + "\n".join(failures)
    )


def test_no_orphan_commands():
    """Every command .md file (excluding _readme, command-registry) must have a matching skill entry."""
    data = _load_skill_registry()
    skill_ids = {s["skill_id"] for s in data.get("skills", []) if "skill_id" in s}
    md_stems = {
        p.stem for p in _CMD_DIR.glob("*.md")
        if p.stem not in _EXCLUDED_STEMS
    }
    orphans = md_stems - skill_ids
    assert not orphans, (
        f"Command .md files with no matching skill entry ({len(orphans)}):\n"
        + "\n".join(sorted(orphans))
    )


def test_routing_registry_skill_references_exist():
    """Every preferred_skill_id in capability-routing-registry must exist in skill-registry."""
    skill_data = _load_skill_registry()
    skill_ids = {s["skill_id"] for s in skill_data.get("skills", []) if "skill_id" in s}

    routing_data = _load_routing_registry()
    routes = routing_data.get("routes", [])
    missing = []
    for route in routes:
        pref = route.get("preferred_skill_id")
        if pref and pref not in skill_ids:
            route_id = route.get("route_id", "<unknown>")
            missing.append(f"route {route_id}: preferred_skill_id={pref!r} not in skill-registry")
    assert not missing, (
        f"Routing routes with dangling preferred_skill_id ({len(missing)}):\n"
        + "\n".join(missing)
    )
