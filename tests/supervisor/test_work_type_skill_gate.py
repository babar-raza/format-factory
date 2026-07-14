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

    def test_rollback_and_recovery_no_longer_a_gap(self):
        """TC-EXT-007-05 (2026-07-14): rollback_and_recovery (SKILL-GAP-011) was
        actually resolved 2026-06-25 (rollback-and-recovery skill registered,
        capability-routing-registry.yaml:498-507 shows current_status: ACTIVE) but
        work-type-skill-map.yaml was never updated to reflect it until this pass.
        Replaces the prior "still open" assertion, which encoded a stale tracking
        bug as if it were ground truth.
        """
        decl = _make_declaration([{
            "item_id": "PROD-001",
            "item_type": "PRODUCT_SOURCE",
            "work_type": "rollback_and_recovery",
        }])
        violations = check_work_type_skill_gate(decl, _REPO)
        assert len(violations) == 0

    def test_blocked_skill_gap_fires_for_a_synthetic_gap(self, tmp_path):
        """Verify the gate mechanism itself still correctly fires when a gap
        exists, independent of the real repo's current gap_mappings (which is
        now empty — see test_gap_mappings_is_currently_empty). Builds an
        isolated fake work-type-skill-map.yaml under tmp_path rather than
        depending on any real gap surviving in the live registry, so this test
        keeps proving the mechanism works even after every real gap is closed.
        """
        import yaml
        fake_map = tmp_path / ".supervisor"
        fake_map.mkdir()
        (fake_map / "work-type-skill-map.yaml").write_text(
            yaml.dump({
                "active_mappings": {"python_api": "add-python-api"},
                "gap_mappings": {
                    "synthetic_test_gap": {
                        "status": "gap",
                        "verdict": "BLOCKED_SKILL_GAP",
                        "gap_register_id": "SKILL-GAP-TEST-001",
                    }
                },
            }),
            encoding="utf-8",
        )
        decl = _make_declaration([{
            "item_id": "PROD-001",
            "item_type": "PRODUCT_SOURCE",
            "work_type": "synthetic_test_gap",
        }])
        violations = check_work_type_skill_gate(decl, tmp_path)
        assert len(violations) == 1
        assert violations[0][0] == "PROD-001"
        assert "BLOCKED_SKILL_GAP" in violations[0][2]

    def test_gap_mappings_is_currently_empty(self):
        """As of this session (TC-EXT-007/009/010), every previously-tracked gap
        (capability_compiler, pre_sprint_governance_hook, rollback_and_recovery)
        has been resolved and moved to active_mappings. This is a factual
        snapshot, not an invariant — a future real gap is expected to repopulate
        gap_mappings, at which point this test should be updated, not deleted.
        """
        import yaml
        raw = yaml.safe_load((_REPO / ".supervisor" / "work-type-skill-map.yaml").read_text(encoding="utf-8"))
        assert raw.get("gap_mappings") == {}

    def test_active_work_type_no_violation(self):
        """work_type=python_api is active — should produce no violation."""
        decl = _make_declaration([{
            "item_id": "PROD-002",
            "item_type": "PRODUCT_SOURCE",
            "work_type": "python_api",
        }])
        violations = check_work_type_skill_gate(decl, _REPO)
        assert len(violations) == 0

    def test_pre_sprint_governance_hook_no_longer_a_gap(self):
        """TC-EXT-010-01/05: pre_sprint_governance_hook was moved from gap_mappings
        to active_mappings (SKILL-GAP-015 closed, /pre-sprint-governance-hook
        skill registered) — must no longer produce a BLOCKED_SKILL_GAP violation.
        """
        decl = _make_declaration([{
            "item_id": "PROD-004",
            "item_type": "PRODUCT_SOURCE",
            "work_type": "pre_sprint_governance_hook",
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

    def test_remaining_gaps_all_detectable(self):
        """Every entry currently present in gap_mappings (whatever it contains
        right now — see test_gap_mappings_is_currently_empty for today's
        snapshot) must produce exactly one violation. Reads the live map
        dynamically rather than hardcoding a work_type list, so this test
        doesn't go stale the next time a gap is opened or closed.

        History of gap_mappings changes this session (2026-07-14):
        - capability_compiler: closed via TC-EXT-009-03 (SKILL-GAP-003)
        - pre_sprint_governance_hook: closed via TC-EXT-010-01/05 (SKILL-GAP-015,
          previously misfiled under SKILL-GAP-008)
        - rollback_and_recovery: closed via TC-EXT-007-05 (SKILL-GAP-011, actually
          resolved 2026-06-25 but never reflected in this map until now)
        Prior history: extract_analytics_from_monolith, ci_transcript_verification,
        supervision_audit — all previously moved to active_mappings.
        """
        import yaml
        raw = yaml.safe_load((_REPO / ".supervisor" / "work-type-skill-map.yaml").read_text(encoding="utf-8"))
        gap_types = list(raw.get("gap_mappings", {}).keys())
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
