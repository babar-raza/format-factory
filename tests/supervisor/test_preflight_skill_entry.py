"""Tests for preflight_skill_entry.py — TC-R008"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from preflight_skill_entry import validate_entry


def test_valid_entry_passes():
    entry = {
        "skill_id": "my-skill",
        "purpose": "Does something useful",
        "command": "/my-skill",
        "status": "active",
    }
    errors = validate_entry(entry)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_missing_command_fails():
    entry = {
        "skill_id": "my-skill",
        "purpose": "Does something useful",
        "status": "active",
        # 'command' intentionally absent
    }
    errors = validate_entry(entry)
    assert any("FIELD_MISSING" in e and "command" in e for e in errors), \
        f"Expected FIELD_MISSING:command, got: {errors}"


def test_invalid_status_fails():
    entry = {
        "skill_id": "my-skill",
        "purpose": "Does something useful",
        "command": "/my-skill",
        "status": "unknown_lifecycle_state",
    }
    errors = validate_entry(entry)
    assert any("STATUS_INVALID" in e for e in errors), \
        f"Expected STATUS_INVALID error, got: {errors}"
