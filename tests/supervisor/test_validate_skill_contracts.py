"""Tests for validate_skill_contracts.py — Skill 4"""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from validate_skill_contracts import validate, _VALID_STATUSES


def test_valid_skill_passes():
    skill = {"skill_id": "test-skill", "purpose": "Test purpose",
              "command": "/test-skill", "status": "active",
              "command_file": ".claude/commands/post-sprint-audit.md"}
    result = validate(skill, _REPO)
    assert result["verdict"] == "PASS"
    assert result["fail_count"] == 0


def test_missing_required_field_fails():
    skill = {"skill_id": "test-skill", "purpose": "", "command": "/test", "status": "active"}
    result = validate(skill, _REPO)
    assert result["verdict"] == "FAIL"
    purpose_fail = any(f["check"] == "required_field:purpose" for f in result["findings"])
    assert purpose_fail


def test_invalid_status_warns():
    skill = {"skill_id": "test-skill", "purpose": "P", "command": "/c", "status": "unknown_status"}
    result = validate(skill, _REPO)
    assert any(f["check"] == "status_enum" and f["result"] == "WARN" for f in result["findings"])


def test_missing_command_file_fails():
    skill = {"skill_id": "test-skill", "purpose": "P", "command": "/c", "status": "active",
             "command_file": ".claude/commands/nonexistent-skill-xyz.md"}
    result = validate(skill, _REPO)
    assert result["verdict"] == "FAIL"
    assert any(f["check"] == "command_file_exists" and f["result"] == "FAIL" for f in result["findings"])


def test_valid_status_values():
    assert "active" in _VALID_STATUSES
    assert "deprecated" in _VALID_STATUSES


def test_main_produces_output(tmp_path):
    import subprocess
    out = tmp_path / "results.yaml"
    result = subprocess.run(
        [sys.executable, str(_REPO / "tools" / "supervisor" / "validate_skill_contracts.py"),
         "--output", str(out)],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert result.returncode == 0
    assert out.exists()
    import yaml
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert "overall_verdict" in data
    assert "total_skills" in data
    assert data["total_skills"] > 0
