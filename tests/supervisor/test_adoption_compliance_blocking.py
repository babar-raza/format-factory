"""Regression tests for Fix 1: adoption_compliance BLOCKING for PRODUCT_SOURCE items.

TC-SGOV-004: When adoption compliance fails for PRODUCT_SOURCE/PRODUCT_TEST items,
the autonomous cycle must set critical_rework_count > 0 and verdict = REWORK_REQUIRED.
Non-product items remain advisory (ACCEPTED_WITH_REWORK).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from validate_adoption_compliance import validate_adoption


def _make_declaration(items):
    return {"planned_work_items": items}


def _make_product_item(item_id, *, skill_id=None, transcript=False, ledger=None, track=None):
    item = {
        "item_id": item_id,
        "title": f"Test item {item_id}",
        "item_type": "PRODUCT_SOURCE",
    }
    if skill_id:
        item["skill_id"] = skill_id
    if transcript:
        item["evidence_paths"] = ["reports/skills-r1/skill-transcripts/test-transcript.json"]
    if ledger:
        item["ledger_entry_id"] = ledger
    if track:
        item["product_track"] = track
    return item


def _make_governance_item(item_id):
    return {
        "item_id": item_id,
        "title": f"Governance item {item_id}",
        "item_type": "GOVERNANCE_TASKCARD",
    }


class TestAdoptionComplianceBlocking:
    """Fix 1: Verify adoption_compliance returns non-compliant for product items without skill provenance."""

    def test_product_item_without_skill_is_non_compliant(self):
        """PRODUCT_SOURCE without skill_id or transcript fails adoption compliance."""
        decl = _make_declaration([
            _make_product_item("PROD-001", track="foss_python"),
        ])
        result = validate_adoption(decl)
        assert not result["compliant"], "Product item without skill_id should fail compliance"

    def test_product_item_with_skill_and_transcript_is_compliant(self):
        """PRODUCT_SOURCE with skill_id and transcript passes."""
        decl = _make_declaration([
            _make_product_item("PROD-002", skill_id="add-python-api",
                               transcript=True, ledger="R1-GOVERNED-TSV-001", track="foss_python"),
        ])
        result = validate_adoption(decl)
        assert result["compliant"], f"Should pass: {result['summary']}"

    def test_governance_item_without_skill_passes(self):
        """GOVERNANCE_TASKCARD without skill_id passes (has implicit exemption)."""
        decl = _make_declaration([
            _make_governance_item("GOV-001"),
        ])
        result = validate_adoption(decl)
        assert result["compliant"], f"Governance items are exempt: {result['summary']}"

    def test_non_compliant_items_identifiable(self):
        """Non-compliant product items can be identified from result['items']."""
        decl = _make_declaration([
            _make_product_item("PROD-003", track="foss_python"),
            _make_governance_item("GOV-002"),
        ])
        result = validate_adoption(decl)
        non_compliant = [
            r for r in result["items"]
            if not r.get("exempt") and not r.get("compliant")
        ]
        assert len(non_compliant) >= 1, "Should have at least 1 non-compliant item"
        assert non_compliant[0]["item_id"] == "PROD-003"

    def test_mixed_product_and_governance_fails_for_product(self):
        """If product item fails but governance passes, overall is non-compliant."""
        decl = _make_declaration([
            _make_product_item("PROD-004", track="foss_python"),
            _make_governance_item("GOV-003"),
        ])
        result = validate_adoption(decl)
        assert not result["compliant"], "Product failure makes overall non-compliant"
