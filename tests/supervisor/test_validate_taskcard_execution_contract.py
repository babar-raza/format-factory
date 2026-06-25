"""
test_validate_taskcard_execution_contract.py — TC-SGF-004 regression tests

5 regression tests for validate_taskcard_execution_contract.py:
  1. valid_taskcard_returns_VALID
  2. taskcard_missing_skill_ids_returns_INVALID
  3. taskcard_missing_allowed_paths_returns_INVALID
  4. taskcard_with_receipt_required_false_returns_INVALID
  5. taskcard_with_empty_skill_ids_list_returns_INVALID (negative control)
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add repo root to sys.path
_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.governance.validate_taskcard_execution_contract import validate


def _write_taskcard(tmp_path: Path, content: dict) -> str:
    """Write a taskcard dict as YAML and return the path string."""
    try:
        import yaml
        text = yaml.dump(content, default_flow_style=False)
    except ImportError:
        # Manual serialization for simple dicts
        lines = ["---"]
        for k, v in content.items():
            if isinstance(v, list):
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
            elif isinstance(v, bool):
                lines.append(f"{k}: {'true' if v else 'false'}")
            else:
                lines.append(f"{k}: {v!r}")
        text = "\n".join(lines) + "\n"

    p = tmp_path / "taskcard.yaml"
    p.write_text(text, encoding="utf-8")
    return str(p)


# TC-SGF-004-T1: Valid taskcard returns VALID
def test_valid_taskcard_returns_VALID(tmp_path):
    """A fully populated mutating taskcard must return verdict=VALID."""
    tc = {
        "task_id": "TC-TEST-001",
        "task_type": "REGISTRY_REPAIR",
        "sprint_types": ["GOVERNANCE_MACHINERY"],
        "required_capabilities": ["read_skill_registry", "add_implementation_paths"],
        "skill_ids": ["normalize-skill-registry"],
        "command_ids": ["/normalize-skill-registry"],
        "allowed_paths": [".supervisor/skill-registry.yaml"],
        "receipt_required": True,
    }
    path = _write_taskcard(tmp_path, tc)
    result = validate(path)
    assert result["verdict"] == "VALID", f"Expected VALID, got: {result}"
    assert result["missing_fields"] == []
    assert result["task_id"] == "TC-TEST-001"


# TC-SGF-004-T2: Taskcard missing skill_ids returns INVALID
def test_taskcard_missing_skill_ids_returns_INVALID(tmp_path):
    """A mutating taskcard without skill_ids must return verdict=INVALID."""
    tc = {
        "task_id": "TC-TEST-002",
        "task_type": "GOVERNANCE_MACHINERY",
        "sprint_types": ["GOVERNANCE_MACHINERY"],
        "required_capabilities": ["read_stuff"],
        # skill_ids intentionally omitted
        "command_ids": ["/some-command"],
        "allowed_paths": [".supervisor/"],
        "receipt_required": True,
    }
    path = _write_taskcard(tmp_path, tc)
    result = validate(path)
    assert result["verdict"] == "INVALID", f"Expected INVALID, got: {result}"
    assert "skill_ids" in result["missing_fields"]


# TC-SGF-004-T3: Taskcard missing allowed_paths returns INVALID
def test_taskcard_missing_allowed_paths_returns_INVALID(tmp_path):
    """A mutating taskcard without allowed_paths must return verdict=INVALID."""
    tc = {
        "task_id": "TC-TEST-003",
        "task_type": "MUTATION_GUARD",
        "sprint_types": ["GOVERNANCE_MACHINERY"],
        "required_capabilities": ["implement_git_pre_commit_hook"],
        "skill_ids": ["enforce-skill-first-execution"],
        "command_ids": ["/enforce-skill-first-execution"],
        # allowed_paths intentionally omitted
        "receipt_required": True,
    }
    path = _write_taskcard(tmp_path, tc)
    result = validate(path)
    assert result["verdict"] == "INVALID", f"Expected INVALID, got: {result}"
    assert "allowed_paths" in result["missing_fields"]


# TC-SGF-004-T4: Taskcard with receipt_required=False returns INVALID
def test_taskcard_with_receipt_required_false_returns_INVALID(tmp_path):
    """receipt_required=False on a mutating taskcard must return INVALID."""
    tc = {
        "task_id": "TC-TEST-004",
        "task_type": "SUPERVISOR_ENFORCEMENT",
        "sprint_types": ["GOVERNANCE_MACHINERY"],
        "required_capabilities": ["add_governance_validator"],
        "skill_ids": ["validate-skill-contracts"],
        "command_ids": ["/validate-skill-contracts"],
        "allowed_paths": ["tools/supervisor/governance_validators.py"],
        "receipt_required": False,  # must be True
    }
    path = _write_taskcard(tmp_path, tc)
    result = validate(path)
    assert result["verdict"] == "INVALID", f"Expected INVALID, got: {result}"
    assert "receipt_required" in result["missing_fields"]


# TC-SGF-004-T5: Negative control — empty skill_ids list returns INVALID
def test_taskcard_with_empty_skill_ids_list_returns_INVALID(tmp_path):
    """Empty skill_ids list must be INVALID (empty ≠ populated)."""
    tc = {
        "task_id": "TC-TEST-005",
        "task_type": "TASKCARD_SCHEMA_REPAIR",
        "sprint_types": ["GOVERNANCE_MACHINERY"],
        "required_capabilities": ["validate_required_fields"],
        "skill_ids": [],  # empty list — must fail
        "command_ids": ["/validate-skill-contracts"],
        "allowed_paths": ["tools/governance/"],
        "receipt_required": True,
    }
    path = _write_taskcard(tmp_path, tc)
    result = validate(path)
    assert result["verdict"] == "INVALID", f"Expected INVALID, got: {result}"
    assert "skill_ids" in result["missing_fields"]
    # Verify error message mentions empty
    error_text = " ".join(result.get("errors", []))
    assert "empty" in error_text.lower() or "skill_ids" in error_text


# Additional: read-only taskcard skips validation (positive VALID via skip)
def test_exempt_task_type_returns_VALID_with_skip_reason(tmp_path):
    """Analysis/read-only task types are exempt from execution contract requirements."""
    tc = {
        "task_id": "TC-TEST-EXEMPT",
        "task_type": "ANALYSIS",
        # No required_capabilities, skill_ids, etc.
    }
    path = _write_taskcard(tmp_path, tc)
    result = validate(path)
    assert result["verdict"] == "VALID", f"Expected VALID, got: {result}"
    assert "skip_reason" in result


# Additional: file-not-found returns INVALID
def test_nonexistent_file_returns_INVALID():
    """A non-existent file path must return INVALID with file error."""
    result = validate("/nonexistent/path/taskcard.yaml")
    assert result["verdict"] == "INVALID"
    assert any("not found" in e.lower() or "not exist" in e.lower() for e in result["errors"])
