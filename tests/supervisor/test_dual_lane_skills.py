"""Tests for dual-lane skill registrations — TC-DL2-013."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

SKILL_REGISTRY = _REPO_ROOT / ".supervisor" / "skill-registry.yaml"
EXPECTED_SKILLS = [
    ("select-deepening-lane", "tools/supervisor/lane_selector.py"),
    ("inventory-format-dom", "tools/supervisor/dom_baseline_scanner.py"),
    ("check-dom-contract", "tools/supervisor/dom_contract_checker.py"),
]


@pytest.fixture(scope="module")
def skills():
    data = yaml.safe_load(SKILL_REGISTRY.read_text(encoding="utf-8"))
    return {s["skill_id"]: s for s in data.get("skills", []) if "skill_id" in s}


class TestDualLaneSkills:

    @pytest.mark.parametrize("skill_id,tool_path", EXPECTED_SKILLS)
    def test_skill_registered(self, skills, skill_id, tool_path):
        """Skill entries parse from skill-registry.yaml."""
        assert skill_id in skills, f"{skill_id} not found in skill registry"

    @pytest.mark.parametrize("skill_id,tool_path", EXPECTED_SKILLS)
    def test_tool_path_exists(self, skills, skill_id, tool_path):
        """Tool implementation files exist on disk."""
        assert (_REPO_ROOT / tool_path).exists(), f"{tool_path} not found"

    @pytest.mark.parametrize("skill_id,tool_path", EXPECTED_SKILLS)
    def test_skill_has_required_fields(self, skills, skill_id, tool_path):
        """Skill entries have required fields."""
        s = skills[skill_id]
        for field in ("command", "purpose", "status", "test_paths"):
            assert field in s, f"{skill_id} missing field: {field}"
        assert s["status"] == "active"

    @pytest.mark.parametrize("skill_id,tool_path", EXPECTED_SKILLS)
    def test_command_file_exists(self, skills, skill_id, tool_path):
        """Active dual-lane skills must have callable command documentation."""
        command_file = skills[skill_id].get("command_file")
        assert command_file, f"{skill_id} missing command_file"
        assert (_REPO_ROOT / command_file).exists(), f"{command_file} not found"
