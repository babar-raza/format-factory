"""Negative tests for the skill registry validator.

Tests that the validator correctly rejects:
- Missing command file
- Missing allowed paths (no handoff fields)
- Missing ledger requirement for src-editing track
- Missing mandatory validations
- Duplicate skill IDs
- Invalid status values
- Short/empty purpose
"""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_skill_registry import validate_registry


def _write_registry(tmp_path: Path, skills: list, **overrides) -> Path:
    data = {
        "registry_id": "test-registry",
        "registry_status": "active_fail_closed",
        "global_controls": {
            "source_edits_require_explicit_handoff": True,
            "exact_path_scope_required": True,
            "product_code_ledger_required_before_source_edit": True,
        },
        "skills": skills,
        **overrides,
    }
    path = tmp_path / "skill-registry.yaml"
    path.write_text(yaml.dump(data), encoding="utf-8")
    return path


def _good_skill(**overrides):
    base = {
        "skill_id": "test-skill",
        "command": "/test-skill",
        "command_file": ".claude/commands/add-dotnet-api.md",
        "status": "active",
        "purpose": "A valid test skill for negative testing purposes.",
        "product_track": "testing",
        "required_handoff_fields": ["field_a", "field_b"],
        "mandatory_validations": ["validation_a"],
    }
    base.update(overrides)
    return base


class TestRegistryValidatorNegative:
    """Negative tests — each should produce at least one error."""

    def test_missing_command_file(self, tmp_path):
        skill = _good_skill(
            command_file=".claude/commands/nonexistent-skill.md",
        )
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("command_file not found" in e for e in result["errors"])

    def test_missing_handoff_fields(self, tmp_path):
        skill = _good_skill(required_handoff_fields=[])
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("required_handoff_fields is empty" in e for e in result["errors"])

    def test_missing_ledger_for_src_editing_track(self, tmp_path):
        skill = _good_skill(
            product_track="commercial_dotnet",
            mandatory_validations=["focused_dotnet_tests"],
        )
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("product_code_ledger_validator" in e for e in result["errors"])
        # Classification must be UNSAFE
        assert result["skills"][0]["classification"] == "UNSAFE"

    def test_missing_mandatory_validations(self, tmp_path):
        skill = _good_skill(mandatory_validations=[])
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("mandatory_validations is empty" in e for e in result["errors"])

    def test_duplicate_skill_ids(self, tmp_path):
        s1 = _good_skill(skill_id="dup-skill")
        s2 = _good_skill(skill_id="dup-skill", command="/dup-skill-2")
        reg = _write_registry(tmp_path, [s1, s2])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("duplicate skill_id" in e for e in result["errors"])

    def test_invalid_status(self, tmp_path):
        skill = _good_skill(status="bogus")
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("invalid status" in e for e in result["errors"])

    def test_short_purpose(self, tmp_path):
        skill = _good_skill(purpose="Short")
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("purpose too short" in e for e in result["errors"])

    def test_empty_skills_list(self, tmp_path):
        reg = _write_registry(tmp_path, [])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("non-empty" in e for e in result["errors"])

    def test_missing_required_field(self, tmp_path):
        skill = _good_skill()
        del skill["purpose"]
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert not result["valid"]
        assert any("missing fields" in e for e in result["errors"])


class TestRegistryValidatorPositive:
    """Positive tests — valid registries should pass."""

    def test_valid_registry_passes(self, tmp_path):
        skill = _good_skill()
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert result["valid"]
        assert result["ready_count"] == 1

    def test_draft_skill_accepted(self, tmp_path):
        skill = _good_skill(
            status="draft",
            command_file=".claude/commands/nonexistent-draft.md",
        )
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert result["valid"]
        assert result["draft_count"] == 1

    def test_real_registry_passes(self, tmp_path):
        real_registry = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        if real_registry.exists():
            result = validate_registry(real_registry, REPO_ROOT)
            assert result["valid"]
            assert result["ready_count"] >= 13

    def test_src_editing_track_with_ledger_passes(self, tmp_path):
        skill = _good_skill(
            product_track="foss_python",
            mandatory_validations=["product_code_ledger_validator", "focused_python_tests"],
        )
        reg = _write_registry(tmp_path, [skill])
        result = validate_registry(reg, REPO_ROOT)
        assert result["valid"]
        assert result["skills"][0]["classification"] == "READY"
