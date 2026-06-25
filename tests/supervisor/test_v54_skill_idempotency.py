"""TC-FL-005: Tests for V69 validate_skill_idempotency_declared + skill registry completeness.

The plan called this 'V54' but V54 was already used; the validator is V69.
This test file is named test_v54 per plan requirement for traceability.

Tests assert:
1. All active skills in skill-registry.yaml have a defined idempotency value (not 'not_specified')
2. V69 WARNs when a work item invokes a skill with idempotency: not_specified
3. V69 PASSes when all invoked skills have declared idempotency
4. V69 is non-blocking (blocks_sprint=False always)
"""

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
sys.path.insert(0, str(_REPO))

import pytest
import yaml


def _load_skills() -> list[dict]:
    path = _REPO / ".supervisor" / "skill-registry.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("skills", [])


_VALID_IDEMPOTENCY_VALUES = {"idempotent", "create_or_update", "state_mutating", "not_applicable"}


class TestSkillRegistryIdempotency:
    """All skills must have a declared idempotency value."""

    def test_no_skills_have_not_specified(self):
        skills = _load_skills()
        not_specified = [s["skill_id"] for s in skills if s.get("idempotency") == "not_specified"]
        assert not_specified == [], (
            f"Skills with idempotency: not_specified (must be fixed): {not_specified}"
        )

    def test_all_active_skills_have_valid_idempotency(self):
        skills = _load_skills()
        invalid = [
            s["skill_id"] for s in skills
            if s.get("status") in ("active", "deprecated")
            and s.get("idempotency") not in _VALID_IDEMPOTENCY_VALUES
        ]
        assert invalid == [], (
            f"Skills with invalid idempotency value: {invalid}. "
            f"Valid values: {_VALID_IDEMPOTENCY_VALUES}"
        )

    def test_idempotency_value_distribution(self):
        """Verify we have a realistic distribution of idempotency values."""
        skills = _load_skills()
        active = [s for s in skills if s.get("status") in ("active",)]
        counts = {}
        for s in active:
            v = s.get("idempotency", "missing")
            counts[v] = counts.get(v, 0) + 1
        # Must have at least one skill in each major category
        assert counts.get("create_or_update", 0) >= 5, "Expected >=5 create_or_update skills"
        assert counts.get("idempotent", 0) >= 3, "Expected >=3 idempotent skills"


class TestV69SkillIdempotencyValidator:
    """V69 validator behavior tests."""

    def _make_decl_with_skill(self, skill_id: str, item_type: str = "PRODUCT_SOURCE") -> dict:
        return {
            "planned_work_items": [{
                "item_id": "TEST-001",
                "item_type": item_type,
                "skill_id": skill_id,
                "title": "Test item",
            }]
        }

    def test_passes_for_known_declared_skill(self):
        from governance_validators_ext import validate_skill_idempotency_declared
        decl = self._make_decl_with_skill("add-python-api")
        result = validate_skill_idempotency_declared(decl, _REPO)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_warns_for_unknown_skill(self):
        """An unknown skill (not in registry) should WARN."""
        from governance_validators_ext import validate_skill_idempotency_declared
        decl = self._make_decl_with_skill("nonexistent-skill-xyz")
        result = validate_skill_idempotency_declared(decl, _REPO)
        # Unknown skill → idempotency=unknown → WARN
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_non_product_items_not_checked(self):
        """Non-PRODUCT_SOURCE items are not checked by V69."""
        from governance_validators_ext import validate_skill_idempotency_declared
        decl = self._make_decl_with_skill("nonexistent-skill-xyz", item_type="DOCUMENTATION")
        result = validate_skill_idempotency_declared(decl, _REPO)
        assert result["result"] == "PASS"

    def test_empty_declaration_passes(self):
        from governance_validators_ext import validate_skill_idempotency_declared
        result = validate_skill_idempotency_declared({}, _REPO)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_validator_never_blocks_sprint(self):
        """V69 must be WARN-only; blocks_sprint must always be False."""
        from governance_validators_ext import validate_skill_idempotency_declared
        decl = {"planned_work_items": [
            {"item_id": f"T-{i}", "item_type": "PRODUCT_SOURCE", "skill_id": "nonexistent-x"}
            for i in range(5)
        ]}
        result = validate_skill_idempotency_declared(decl, _REPO)
        assert result["blocks_sprint"] is False

    def test_v69_registered_in_runner(self):
        """V69 must be wired into run_all_governance_validators."""
        from governance_validator_runner import run_all_governance_validators
        decl = {"planned_work_items": []}
        output = run_all_governance_validators(decl, _REPO)
        # run_all_governance_validators returns a dict with a 'validators' list
        validator_names = [r["validator"] for r in output.get("validators", [])]
        assert "validate_skill_idempotency_declared" in validator_names, (
            "V69 must be registered in run_all_governance_validators"
        )
