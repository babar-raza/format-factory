"""Tests for semantic spec-parity validators — 2 tests per validator (pass + fail).

TC-GAP-A02: AttributePropertyMap, Containment, Alias, SkillWiring validators.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.requirements_authority.spec_parity_validators import (
    AttributePropertyMapValidator,
    ContainmentGraphValidator,
    AliasCompatibilityValidator,
    SkillWiringValidator,
)


# ── AttributePropertyMapValidator ──────────────────────────────────────────

class TestAttributePropertyMapValidator:
    def test_pass_valid_refs(self):
        facts = [{"qname": "FODS-FACT-001"}, {"qname": "FODS-FACT-002"}]
        cap_map = {
            "attributes": [
                {"name": "cell_type", "spec_fact_ref": "FODS-FACT-001"},
                {"name": "sheet_name", "spec_fact_ref": "FODS-FACT-002"},
            ]
        }
        result = AttributePropertyMapValidator().validate(facts, cap_map)
        assert result.passed is True
        assert len(result.evidence) == 2

    def test_fail_unknown_ref(self):
        facts = [{"qname": "FODS-FACT-001"}]
        cap_map = {
            "attributes": [
                {"name": "cell_type", "spec_fact_ref": "NONEXISTENT-FACT"},
            ]
        }
        result = AttributePropertyMapValidator().validate(facts, cap_map)
        assert result.passed is False
        assert any("NONEXISTENT-FACT" in f for f in result.failures)


# ── ContainmentGraphValidator ──────────────────────────────────────────────

class TestContainmentGraphValidator:
    def test_pass_valid_containment(self):
        facts = [{"qname": "ODF-SHEET-FACT-TABLE"}, {"qname": "ODF-SHEET-FACT-ROW"}]
        cap_map = {
            "containment": [
                {
                    "parent": "table:table",
                    "child": "table:table-row",
                    "parent_fact_ref": "ODF-SHEET-FACT-TABLE",
                    "child_fact_ref": "ODF-SHEET-FACT-ROW",
                }
            ]
        }
        result = ContainmentGraphValidator().validate(facts, cap_map)
        assert result.passed is True

    def test_fail_missing_parent_ref(self):
        facts = [{"qname": "ODF-SHEET-FACT-ROW"}]
        cap_map = {
            "containment": [
                {
                    "parent": "table:table",
                    "child": "table:table-row",
                    "parent_fact_ref": "MISSING-FACT",
                    "child_fact_ref": "ODF-SHEET-FACT-ROW",
                }
            ]
        }
        result = ContainmentGraphValidator().validate(facts, cap_map)
        assert result.passed is False
        assert any("MISSING-FACT" in f for f in result.failures)


# ── AliasCompatibilityValidator ────────────────────────────────────────────

class TestAliasCompatibilityValidator:
    def test_pass_consistent_aliases(self):
        facts = []
        cap_map = {
            "aliases": [
                {"facade": "FodsCell", "canonical": "Table.TableCell"},
                {"facade": "FodsSheet", "canonical": "Table.Table"},
            ]
        }
        result = AliasCompatibilityValidator().validate(facts, cap_map)
        assert result.passed is True
        assert len(result.evidence) == 2

    def test_fail_conflicting_aliases(self):
        facts = []
        cap_map = {
            "aliases": [
                {"facade": "FodsCell", "canonical": "Table.TableCell"},
                {"facade": "FodsCell", "canonical": "Table.DifferentCell"},
            ]
        }
        result = AliasCompatibilityValidator().validate(facts, cap_map)
        assert result.passed is False
        assert any("FodsCell" in f for f in result.failures)


# ── SkillWiringValidator ───────────────────────────────────────────────────

class TestSkillWiringValidator:
    def test_pass_all_skills_registered(self):
        facts = []
        cap_map = {
            "registered_skills": ["add-python-object-model-feature", "add-dogfood-export"],
            "skill_references": ["add-python-object-model-feature"],
        }
        result = SkillWiringValidator().validate(facts, cap_map)
        assert result.passed is True

    def test_fail_unregistered_skill(self):
        facts = []
        cap_map = {
            "registered_skills": ["add-python-object-model-feature"],
            "skill_references": ["add-python-object-model-feature", "nonexistent-skill"],
        }
        result = SkillWiringValidator().validate(facts, cap_map)
        assert result.passed is False
        assert any("nonexistent-skill" in f for f in result.failures)
