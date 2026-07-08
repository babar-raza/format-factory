"""Regression tests for Fix 2: work-type-skill-map.yaml runtime gate.

TC-SGOV-005: check_work_type_skill_gate reads the YAML map and returns
BLOCKED_SKILL_GAP violations for PRODUCT items whose work_type maps to a gap.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from validate_adoption_compliance import check_work_type_skill_gate


def _make_declaration(items):
    return {"planned_work_items": items}


class TestWorkTypeSkillGate:
    """Fix 2: Verify work-type-skill-map.yaml is read at runtime."""

    def test_blocked_skill_gap_fires_for_capability_compiler(self):
        """work_type=capability_compiler is a known gap — must produce violation."""
        decl = _make_declaration([{
            "item_id": "PROD-001",
            "item_type": "PRODUCT_SOURCE",
            "work_type": "capability_compiler",
        }])
        violations = check_work_type_skill_gate(decl, _REPO)
        assert len(violations) == 1
        assert violations[0][0] == "PROD-001"
        assert "BLOCKED_SKILL_GAP" in violations[0][2]

    def test_active_work_type_no_violation(self):
        """work_type=python_api is active — should produce no violation."""
        decl = _make_declaration([{
            "item_id": "PROD-002",
            "item_type": "PRODUCT_SOURCE",
            "work_type": "python_api",
        }])
        violations = check_work_type_skill_gate(decl, _REPO)
        assert len(violations) == 0

    def test_governance_item_skipped(self):
        """GOVERNANCE_TASKCARD items are not checked against skill map."""
        decl = _make_declaration([{
            "item_id": "GOV-001",
            "item_type": "GOVERNANCE_TASKCARD",
            "work_type": "capability_compiler",
        }])
        violations = check_work_type_skill_gate(decl, _REPO)
        assert len(violations) == 0

    def test_missing_work_type_is_not_violation(self):
        """Items without work_type field are skipped (advisory, not blocking)."""
        decl = _make_declaration([{
            "item_id": "PROD-003",
            "item_type": "PRODUCT_SOURCE",
        }])
        violations = check_work_type_skill_gate(decl, _REPO)
        assert len(violations) == 0

    def test_all_five_gaps_detected(self):
        """All 5 BLOCKED_SKILL_GAP entries in map are detectable.

        Note: extract_analytics_from_monolith was moved to active_mappings when
        SKILL-GAP-005 was closed; replaced with rollback_and_recovery (SKILL-GAP-011).
        """
        gap_types = [
            "capability_compiler",
            "rollback_and_recovery",
            "pre_sprint_governance_hook",
            "ci_transcript_verification",
            "supervision_audit",
        ]
        for i, wt in enumerate(gap_types):
            decl = _make_declaration([{
                "item_id": f"GAP-{i}",
                "item_type": "PRODUCT_SOURCE",
                "work_type": wt,
            }])
            violations = check_work_type_skill_gate(decl, _REPO)
            assert len(violations) == 1, f"Gap {wt} should produce exactly 1 violation"
            assert "BLOCKED_SKILL_GAP" in violations[0][2], f"Gap {wt} must be BLOCKED_SKILL_GAP"

    def test_empty_declaration(self):
        """Empty declaration produces no violations."""
        violations = check_work_type_skill_gate({"planned_work_items": []}, _REPO)
        assert violations == []

    def test_missing_skill_map_file(self):
        """If work-type-skill-map.yaml doesn't exist, return SKILL_MAP_MISSING."""
        violations = check_work_type_skill_gate(
            _make_declaration([{"item_id": "X", "item_type": "PRODUCT_SOURCE", "work_type": "python_api"}]),
            Path("/nonexistent/repo"),
        )
        assert len(violations) == 1
        assert violations[0][2] == "SKILL_MAP_MISSING"
