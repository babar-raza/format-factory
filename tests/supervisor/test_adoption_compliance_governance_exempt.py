"""Tests for governance item type exemption in adoption compliance.

GRH-TC-004: Lane D — validate_adoption_compliance.py must recognize GOVERNANCE_DOC,
GOVERNANCE_SCHEMA, LEGACY_BACKFILL_METADATA item_type and exception_classification
(investigation_only, legacy_backfill) as implicit exemptions from transcript/skill_id
requirements.

Before the fix: strict_fail=True for governance sprints (10 items, 0 transcripts, 0 exemptions).
After the fix: governance items count as explicitly exempt → PASS_WITH_EXEMPTIONS.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _governance_item(item_id: str, item_type: str = "GOVERNANCE_DOC",
                     exc_class: str = "investigation_only") -> dict:
    return {
        "item_id": item_id,
        "title": f"Governance item {item_id}",
        "item_type": item_type,
        "exception_classification": exc_class,
    }


def _product_item(item_id: str, track: str = "foss_python") -> dict:
    return {
        "item_id": item_id,
        "title": f"Product item {item_id}",
        "item_type": "PRODUCT_SOURCE",
        "product_track": track,
    }


class TestHasExplicitExemption:
    """_has_explicit_exemption should recognize governance markers."""

    def test_exemption_reason_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"exemption_reason": "not applicable"})

    def test_transcript_exemption_reason_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"transcript_exemption_reason": "governance doc"})

    def test_governance_doc_item_type_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"item_type": "GOVERNANCE_DOC"})

    def test_governance_schema_item_type_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"item_type": "GOVERNANCE_SCHEMA"})

    def test_legacy_backfill_item_type_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"item_type": "LEGACY_BACKFILL_METADATA"})

    def test_governance_policy_item_type_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"item_type": "GOVERNANCE_POLICY"})

    def test_governance_taskcard_item_type_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"item_type": "GOVERNANCE_TASKCARD"})

    def test_investigation_only_exception_classification_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"exception_classification": "investigation_only"})

    def test_legacy_backfill_exception_classification_recognized(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert _has_explicit_exemption({"exception_classification": "legacy_backfill"})

    def test_product_source_not_exempt(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert not _has_explicit_exemption({"item_type": "PRODUCT_SOURCE"})

    def test_empty_item_not_exempt(self):
        from validate_adoption_compliance import _has_explicit_exemption
        assert not _has_explicit_exemption({})


class TestGovernanceSprintAdoptionCompliance:
    """Governance sprints should pass adoption compliance."""

    def test_governance_sprint_passes_compliance(self):
        from validate_adoption_compliance import validate_adoption
        declaration = {
            "planned_work_items": [
                _governance_item(f"GR-TC-{i:03d}", "GOVERNANCE_DOC", "investigation_only")
                for i in range(1, 11)
            ]
        }
        result = validate_adoption(declaration)
        assert result["compliant"] is True, (
            f"Expected compliant=True for governance sprint, got: {result['compliance_classification']}"
        )

    def test_governance_sprint_passes_with_exemptions(self):
        from validate_adoption_compliance import validate_adoption, COMPLIANCE_PASS_WITH_EXEMPTIONS
        declaration = {
            "planned_work_items": [
                _governance_item("GR-TC-001", "GOVERNANCE_DOC", "investigation_only")
            ]
        }
        result = validate_adoption(declaration)
        assert result["compliance_classification"] == COMPLIANCE_PASS_WITH_EXEMPTIONS

    def test_legacy_backfill_sprint_passes(self):
        from validate_adoption_compliance import validate_adoption
        declaration = {
            "planned_work_items": [
                _governance_item("GR-TC-006", "LEGACY_BACKFILL_METADATA", "legacy_backfill")
            ]
        }
        result = validate_adoption(declaration)
        assert result["compliant"] is True

    def test_strict_fail_not_triggered_for_governance(self):
        from validate_adoption_compliance import validate_adoption
        declaration = {
            "planned_work_items": [
                _governance_item(f"GR-TC-{i:03d}", "GOVERNANCE_DOC", "investigation_only")
                for i in range(1, 11)
            ]
        }
        result = validate_adoption(declaration)
        assert result["strict_fail"] is False, "strict_fail should be False for governance items"

    def test_product_sprint_still_fails_without_transcripts(self):
        from validate_adoption_compliance import validate_adoption, COMPLIANCE_FAIL_MISSING_TRANSCRIPTS
        declaration = {
            "planned_work_items": [
                _product_item("TC-PRODUCT-001"),
                _product_item("TC-PRODUCT-002"),
            ]
        }
        result = validate_adoption(declaration)
        # Product items with SRC_EDITING_TRACKS require transcripts — should fail
        # (foss_python is in SRC_EDITING_TRACKS)
        assert result["compliant"] is False
        assert result["compliance_classification"] in (
            COMPLIANCE_FAIL_MISSING_TRANSCRIPTS,
            "FAIL_MISSING_SKILL_IDS",
            "FAIL_MISSING_LEDGER",
        )

    def test_items_with_explicit_exemption_reason_still_pass(self):
        from validate_adoption_compliance import validate_adoption
        declaration = {
            "planned_work_items": [
                {
                    "item_id": "TC-001",
                    "title": "Some product item",
                    "item_type": "PRODUCT_SOURCE",
                    "exemption_reason": "metadata-only change, no source modification",
                }
            ]
        }
        result = validate_adoption(declaration)
        assert result["items_with_explicit_exemption"] == 1


class TestRealGovernanceSprint:
    """Verify the real governance sprint now passes adoption compliance."""

    def test_real_governance_sprint_passes_adoption_compliance(self):
        decl_path = REPO_ROOT / ".local/evidences/governance-repeatability-contracts-001/evidence-declaration.yaml"
        if not decl_path.exists():
            pytest.skip("Governance declaration not found")
        import yaml
        from validate_adoption_compliance import validate_adoption
        with open(decl_path, encoding="utf-8") as f:
            decl = yaml.safe_load(f)
        result = validate_adoption(decl)
        assert result["compliant"] is True, (
            f"Real governance sprint should pass adoption compliance. "
            f"Got: {result['compliance_classification']}. "
            f"strict_fail={result['strict_fail']}, "
            f"items_with_explicit_exemption={result['items_with_explicit_exemption']}"
        )
