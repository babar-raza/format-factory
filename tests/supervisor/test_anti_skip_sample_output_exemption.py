"""Tests for anti-skip sample-output exemption for governance sprints (Lane C, GRE-TC-003).

Verifies:
- governance-only sprint does not trigger missing_sample_outputs violation
- product-source sprint still triggers violation when sample outputs missing
- legacy backfill metadata does not trigger violation
- dry-run fixture classification exempts from requirement
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestGovernanceSprintExemption:
    """Governance-only sprints must not trigger missing_sample_outputs violation."""

    def test_governance_doc_sprint_exempt(self):
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {
            "planned_work_items": [
                {"item_id": "GR-TC-001", "item_type": "GOVERNANCE_DOC",
                 "exception_classification": "investigation_only"},
            ]
        }
        result = detect_missing_sample_outputs(
            evidence_root=REPO_ROOT / ".local/evidences/test-anti-skip",
            declaration=decl,
        )
        assert not result["is_violation"], (
            f"Governance-only sprint should not violate sample output requirement: {result}"
        )
        assert result.get("exemption") == "governance_or_no_product_source"

    def test_governance_schema_sprint_exempt(self):
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {
            "planned_work_items": [
                {"item_id": "GR-TC-005", "item_type": "GOVERNANCE_SCHEMA"},
                {"item_id": "GR-TC-006", "item_type": "LEGACY_BACKFILL_METADATA",
                 "exception_classification": "legacy_backfill"},
            ]
        }
        result = detect_missing_sample_outputs(
            evidence_root=REPO_ROOT / ".local/evidences/test-anti-skip",
            declaration=decl,
        )
        assert not result["is_violation"]

    def test_investigation_only_exception_exempt(self):
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {
            "planned_work_items": [
                {"item_id": "TC-001", "item_type": "PRODUCT_SOURCE",
                 "exception_classification": "investigation_only"},
            ]
        }
        result = detect_missing_sample_outputs(
            evidence_root=REPO_ROOT / ".local/evidences/test-anti-skip",
            declaration=decl,
        )
        # investigation_only exception makes the sprint governance-like
        assert not result["is_violation"]

    def test_legacy_backfill_sprint_exempt(self):
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {
            "planned_work_items": [
                {"item_id": "GR-TC-006", "item_type": "LEGACY_BACKFILL_METADATA",
                 "exception_classification": "legacy_backfill"},
            ]
        }
        result = detect_missing_sample_outputs(
            evidence_root=REPO_ROOT / ".local/evidences/test-anti-skip",
            declaration=decl,
        )
        assert not result["is_violation"]

    def test_empty_declaration_exempt(self):
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {"planned_work_items": []}
        result = detect_missing_sample_outputs(
            evidence_root=REPO_ROOT / ".local/evidences/test-anti-skip",
            declaration=decl,
        )
        # No items → no PRODUCT_SOURCE → exempt
        assert not result["is_violation"]

    def test_dry_run_fixture_exempt(self):
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {
            "planned_work_items": [
                {"item_id": "TC-DRY", "item_type": "PRODUCT_SOURCE",
                 "exception_classification": "dry_run_fixture"},
            ]
        }
        result = detect_missing_sample_outputs(
            evidence_root=REPO_ROOT / ".local/evidences/test-anti-skip",
            declaration=decl,
        )
        assert not result["is_violation"]


class TestProductSourceStillRequiresSampleOutputs:
    """PRODUCT_SOURCE items still trigger violation when sample outputs missing."""

    def test_product_source_sprint_violates_when_no_outputs(self, tmp_path):
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {
            "planned_work_items": [
                {"item_id": "TC-PROD-001", "item_type": "PRODUCT_SOURCE",
                 "format_id": "gnumeric"},
            ]
        }
        # No sample-outputs dir in tmp_path
        result = detect_missing_sample_outputs(
            evidence_root=tmp_path,
            declaration=decl,
        )
        assert result["is_violation"], (
            "PRODUCT_SOURCE sprint without sample outputs should be a violation"
        )

    def test_mixed_sprint_still_requires_outputs(self, tmp_path):
        """Sprint with PRODUCT_SOURCE + GOVERNANCE_DOC still requires sample outputs."""
        from anti_skip_checker import detect_missing_sample_outputs
        decl = {
            "planned_work_items": [
                {"item_id": "TC-PROD-001", "item_type": "PRODUCT_SOURCE"},
                {"item_id": "GR-TC-001", "item_type": "GOVERNANCE_DOC",
                 "exception_classification": "investigation_only"},
            ]
        }
        result = detect_missing_sample_outputs(
            evidence_root=tmp_path,
            declaration=decl,
        )
        assert result["is_violation"], "Mixed sprint with PRODUCT_SOURCE still needs outputs"


class TestIsGovernanceOnlySprint:
    """Test the governance-only sprint detection helper."""

    def test_governance_doc_is_governance_only(self):
        from anti_skip_checker import _is_governance_only_sprint
        decl = {"planned_work_items": [
            {"item_type": "GOVERNANCE_DOC", "exception_classification": "investigation_only"}
        ]}
        assert _is_governance_only_sprint(decl) is True

    def test_product_source_is_not_governance_only(self):
        from anti_skip_checker import _is_governance_only_sprint
        decl = {"planned_work_items": [
            {"item_type": "PRODUCT_SOURCE"}
        ]}
        assert _is_governance_only_sprint(decl) is False

    def test_none_declaration_is_not_governance_only(self):
        from anti_skip_checker import _is_governance_only_sprint
        assert _is_governance_only_sprint(None) is False

    def test_empty_items_is_not_governance_only(self):
        from anti_skip_checker import _is_governance_only_sprint
        decl = {"planned_work_items": []}
        assert _is_governance_only_sprint(decl) is False

    def test_real_sprint2_declaration_is_governance_only(self):
        """Sprint 2 governance declaration should be detected as governance-only."""
        import yaml
        from anti_skip_checker import _is_governance_only_sprint
        decl_path = (
            REPO_ROOT / ".local/evidences/governance-repeatability-hardening-rnext"
            / "evidence-declaration.yaml"
        )
        if not decl_path.exists():
            pytest.skip("Sprint 2 declaration not found")
        with open(decl_path, encoding="utf-8") as f:
            decl = yaml.safe_load(f)
        assert _is_governance_only_sprint(decl) is True


class TestHasProductSourceItems:
    """Test the product-source detection helper."""

    def test_product_source_detected(self):
        from anti_skip_checker import _has_product_source_items
        decl = {"planned_work_items": [{"item_type": "PRODUCT_SOURCE"}]}
        assert _has_product_source_items(decl) is True

    def test_governance_doc_not_product_source(self):
        from anti_skip_checker import _has_product_source_items
        decl = {"planned_work_items": [{"item_type": "GOVERNANCE_DOC"}]}
        assert _has_product_source_items(decl) is False

    def test_dry_run_fixture_not_product_source(self):
        from anti_skip_checker import _has_product_source_items
        decl = {"planned_work_items": [
            {"item_type": "PRODUCT_SOURCE", "exception_classification": "dry_run_fixture"}
        ]}
        assert _has_product_source_items(decl) is False
