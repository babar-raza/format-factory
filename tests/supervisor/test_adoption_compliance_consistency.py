"""
tests/supervisor/test_adoption_compliance_consistency.py

Lane 5 — Sprint FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001

Tests that adoption compliance correctly distinguishes:
  - PASS / PASS_WITH_EXEMPTIONS (advisory only, does not block)
  - FAIL_MISSING_TRANSCRIPTS (advisory warning in non-product-track sprints)

Guards against the AF-004 contradiction:
  "adoption compliance top-level FAIL_MISSING_TRANSCRIPTS but autonomous-cycle exits 0"

Key rule verified: all non-exempt items without transcripts or skill_ids MUST have
explicit exemption_reason to avoid FAIL_MISSING_TRANSCRIPTS.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from validate_adoption_compliance import (
    validate_adoption,
    COMPLIANCE_PASS,
    COMPLIANCE_PASS_WITH_EXEMPTIONS,
    COMPLIANCE_FAIL_MISSING_TRANSCRIPTS,
    COMPLIANCE_FAIL_MISSING_SKILL_IDS,
    COMPLIANCE_FAIL_MISSING_LEDGER,
    _is_exempt,
    _is_non_source_changing,
    _has_explicit_exemption,
)


# ---------------------------------------------------------------------------
# _is_exempt
# ---------------------------------------------------------------------------

class TestIsExempt:
    def test_exempt_by_prefix_W0(self):
        assert _is_exempt({"item_id": "W0-001", "title": "Something"}) is True

    def test_exempt_by_title_preflight(self):
        assert _is_exempt({"item_id": "X-001", "title": "Preflight check"}) is True

    def test_exempt_by_title_closeout(self):
        assert _is_exempt({"item_id": "X-002", "title": "Final Closeout"}) is True

    def test_not_exempt_normal_item(self):
        assert _is_exempt({"item_id": "WI-001", "title": "Implement write_gnumeric"}) is False


# ---------------------------------------------------------------------------
# _has_explicit_exemption
# ---------------------------------------------------------------------------

class TestHasExplicitExemption:
    def test_exemption_reason_field(self):
        assert _has_explicit_exemption({"exemption_reason": "Supervisor repair"}) is True

    def test_transcript_exemption_reason_field(self):
        assert _has_explicit_exemption({"transcript_exemption_reason": "No skill needed"}) is True

    def test_no_exemption(self):
        assert _has_explicit_exemption({"item_id": "X"}) is False

    def test_empty_string_not_exemption(self):
        assert _has_explicit_exemption({"exemption_reason": ""}) is False


# ---------------------------------------------------------------------------
# validate_adoption — PASS cases
# ---------------------------------------------------------------------------

class TestValidateAdoptionPass:
    """Items with explicit exemptions pass as PASS_WITH_EXEMPTIONS."""

    def _make_supervisor_repair_item(self, item_id: str, title: str) -> dict:
        return {
            "item_id": item_id,
            "title": title,
            "status": "IMPLEMENTED",
            "exemption_reason": "supervisor-tier tooling repair; no skill invocation required",
        }

    def test_all_items_exempted_pass_with_exemptions(self):
        decl = {
            "planned_work_items": [
                self._make_supervisor_repair_item("L1-001", "Wire evidence_continuation"),
                self._make_supervisor_repair_item("L2-001", "Fix next-work-items safety"),
                self._make_supervisor_repair_item("L3-001", "Queue replenishment repair"),
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is True
        assert result["compliance_classification"] == COMPLIANCE_PASS_WITH_EXEMPTIONS

    def test_empty_planned_items_is_pass(self):
        decl = {"planned_work_items": []}
        result = validate_adoption(decl)
        assert result["compliant"] is True

    def test_all_exempt_items_pass(self):
        decl = {
            "planned_work_items": [
                {"item_id": "W0-001", "title": "Preflight"},
                {"item_id": "W9-FINAL-001", "title": "Final closeout"},
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is True

    def test_items_with_transcript_pass(self):
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-001",
                    "title": "Implement write_gnumeric",
                    "skill_id": "add-python-api",
                    "evidence_paths": ["reports/skills/transcript-001.json"],
                }
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is True


# ---------------------------------------------------------------------------
# validate_adoption — FAIL cases
# ---------------------------------------------------------------------------

class TestValidateAdoptionFail:
    """Items without exemption, transcript, or skill_id fail strictly."""

    def test_no_exemption_no_transcript_no_skill_fails(self):
        """STRICT RULE: non-exempt items without transcripts/skill_ids/exemptions fail."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-001",
                    "title": "Add gnumeric feature",
                    "status": "IMPLEMENTED",
                    # No exemption_reason, no skill_id, no transcript
                }
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is False
        assert result["compliance_classification"] == COMPLIANCE_FAIL_MISSING_TRANSCRIPTS

    def test_src_editing_track_without_ledger_fails(self):
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-002",
                    "title": "Implement write_abw",
                    "product_track": "foss_python",
                    "skill_id": "add-python-api",
                    "evidence_paths": ["reports/skills/transcript-001.json"],
                    # No ledger_entry_id, no exemption_reason
                }
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is False
        assert result["compliance_classification"] == COMPLIANCE_FAIL_MISSING_LEDGER

    def test_compliance_classification_is_string(self):
        decl = {"planned_work_items": []}
        result = validate_adoption(decl)
        assert isinstance(result["compliance_classification"], str)


# ---------------------------------------------------------------------------
# AF-004 specific: exemption_reason resolves FAIL_MISSING_TRANSCRIPTS
# ---------------------------------------------------------------------------

class TestAF004ExemptionResolution:
    """
    AF-004 fix: a supervisor-tier sprint should pass adoption compliance
    by using exemption_reason on all non-exempt items.
    """

    def test_sprint10_style_declaration_passes(self):
        """Simulate Sprint 10 evidence declaration — all supervisor work items
        with exemption_reason — must produce PASS_WITH_EXEMPTIONS not FAIL."""
        items = [
            {
                "item_id": "L1-CONTINUATION-SIGNAL",
                "title": "Wire evidence_continuation into autonomous_cycle.py",
                "status": "IMPLEMENTED",
                "exemption_reason": "supervisor-tier tooling repair; no skill invocation required",
            },
            {
                "item_id": "L2-NEXT-WORK-SAFETY",
                "title": "Fix next-work-items external-gate classification",
                "status": "IMPLEMENTED",
                "exemption_reason": "supervisor-tier tooling repair; no skill invocation required",
            },
            {
                "item_id": "L3-QUEUE-REPLENISHMENT",
                "title": "Seed post-closeout queue item after sprint closeout",
                "status": "IMPLEMENTED",
                "exemption_reason": "supervisor-tier tooling repair; no skill invocation required",
            },
            {
                "item_id": "L4-PROOF",
                "title": "Proof: machine-readable next action executes via next_action_runner",
                "status": "IMPLEMENTED",
                "exemption_reason": "proof documentation; no skill invocation required",
            },
        ]
        decl = {"planned_work_items": items}
        result = validate_adoption(decl)
        assert result["compliant"] is True, (
            f"Sprint 10 style declaration should be compliant: {result['summary']}"
        )
        assert result["compliance_classification"] != COMPLIANCE_FAIL_MISSING_TRANSCRIPTS, (
            f"Must not be FAIL_MISSING_TRANSCRIPTS: {result['compliance_classification']}"
        )
        assert result["compliance_classification"] == COMPLIANCE_PASS_WITH_EXEMPTIONS

    def test_mixed_exempted_and_non_exempted_detects_fail(self):
        """If ANY non-exempt item lacks exemption+transcript+skill_id, it should fail."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "L1",
                    "title": "Fix autonomous_cycle.py",
                    "exemption_reason": "supervisor repair",
                },
                {
                    "item_id": "L2",
                    "title": "New product feature without exemption",
                    # No exemption_reason, no transcript, no skill_id → will trigger strict fail
                },
            ]
        }
        result = validate_adoption(decl)
        # strict_fail should trigger because L2 has no transcript/skill_id/exemption
        assert result["compliant"] is False

    def test_result_has_summary_field(self):
        decl = {"planned_work_items": []}
        result = validate_adoption(decl)
        assert "summary" in result
        assert isinstance(result["summary"], str)

    def test_result_has_compliant_field(self):
        decl = {"planned_work_items": []}
        result = validate_adoption(decl)
        assert "compliant" in result
        assert isinstance(result["compliant"], bool)

    def test_result_has_non_exempt_items_count(self):
        decl = {"planned_work_items": [
            {"item_id": "W0-001", "title": "Preflight"},
            {"item_id": "WI-001", "title": "Do work", "exemption_reason": "x"},
        ]}
        result = validate_adoption(decl)
        assert "non_exempt_items" in result
        assert result["non_exempt_items"] == 1  # Only WI-001 is non-exempt
