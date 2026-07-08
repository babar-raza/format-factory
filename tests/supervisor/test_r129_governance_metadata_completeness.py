"""
test_r129_governance_metadata_completeness.py
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-GOVERNANCE-CLOSURE-REPEATABILITY-AND-BACKFILL-001
Added: 2026-06-08

Regression tests verifying:
- PRODUCT_SOURCE work items have required governance metadata
  (execution_method, source_diff_paths, idempotency_key)
- Adoption compliance passes when all items have proper item_types or exemptions
- Lane execution ledger is discoverable by anti-skip
- PPM P3->P4 promotion is live
- Format authority matrix is consistent
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import (
    validate_execution_method_required,
    validate_idempotency_key_required,
    validate_source_diff_required,
    validate_spec_fact_refs_wired,
)
from validate_adoption_compliance import validate_adoption
from anti_skip_checker import detect_missing_lane_ledger
from authority_gate_validation import validate_format_authority


class TestGovernanceMetadataCompleteness:
    """PRODUCT_SOURCE items must carry execution_method, source_diff_paths, idempotency_key."""

    def test_product_source_without_execution_method_fails(self):
        """Governance validator must FAIL when PRODUCT_SOURCE item is missing execution_method."""
        bad_decl = {
            "planned_work_items": [
                {"item_id": "WI-BAD-1", "item_type": "PRODUCT_SOURCE", "title": "Missing metadata", "status": "completed"}
            ]
        }
        result = validate_execution_method_required(bad_decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_product_source_with_backfilled_execution_method_passes(self):
        """BACKFILLED_LEGACY_EXECUTION is a valid execution_method for governance validators."""
        good_decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-GOOD-1",
                    "item_type": "PRODUCT_SOURCE",
                    "title": "Properly governed item",
                    "status": "completed",
                    "execution_method": "BACKFILLED_LEGACY_EXECUTION",
                    "source_diff_paths": ["src/python/fods/constants.py"],
                    "idempotency_key": "a" * 64,
                }
            ]
        }
        em = validate_execution_method_required(good_decl)
        sd = validate_source_diff_required(good_decl)
        ik = validate_idempotency_key_required(good_decl)
        assert em["result"] != "FAIL", f"execution_method should pass: {em}"
        assert sd["result"] != "FAIL", f"source_diff should pass: {sd}"
        assert ik["result"] != "FAIL", f"idempotency_key should pass: {ik}"

    def test_governance_doc_items_exempt_from_execution_method(self):
        """GOVERNANCE_DOC items are exempt from execution_method requirement."""
        decl = {
            "planned_work_items": [
                {"item_id": "WI-GOV-1", "item_type": "GOVERNANCE_DOC", "title": "Governance analysis", "status": "completed"},
                {"item_id": "WI-GOV-2", "item_type": "GOVERNANCE_SCHEMA", "title": "Schema update", "status": "completed"},
            ]
        }
        result = validate_execution_method_required(decl)
        assert result["result"] != "FAIL"

    def test_spec_authority_items_exempt_from_execution_method(self):
        """SPEC_AUTHORITY items are not in PRODUCT_SOURCE_ITEM_TYPES so are exempt."""
        decl = {
            "planned_work_items": [
                {"item_id": "WI-SA-1", "item_type": "SPEC_AUTHORITY", "title": "Format backfill", "status": "completed"},
            ]
        }
        result = validate_execution_method_required(decl)
        assert result["result"] != "FAIL"

    def test_missing_idempotency_key_blocks_sprint(self):
        """Missing idempotency_key on PRODUCT_SOURCE item blocks sprint."""
        bad_decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-BAD-2",
                    "item_type": "PRODUCT_SOURCE",
                    "title": "Missing idempotency",
                    "status": "completed",
                    "execution_method": "BACKFILLED_LEGACY_EXECUTION",
                    "source_diff_paths": ["src/python/foo.py"],
                }
            ]
        }
        result = validate_idempotency_key_required(bad_decl)
        assert result["result"] == "FAIL"


class TestAdoptionComplianceRules:
    """Adoption compliance must pass when all items have proper types or exemptions."""

    def test_all_governance_doc_items_compliance_passes(self):
        """Sprint with all GOVERNANCE_DOC items must pass adoption compliance."""
        decl = {
            "planned_work_items": [
                {"item_id": "WI-G1", "item_type": "GOVERNANCE_DOC", "title": "Lane 1", "status": "completed"},
                {"item_id": "WI-G2", "item_type": "GOVERNANCE_DOC", "title": "Lane 2", "status": "completed"},
                {"item_id": "WI-G3", "item_type": "GOVERNANCE_DOC", "title": "Lane 3", "status": "completed"},
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is True
        assert result["strict_fail"] is False

    def test_spec_authority_with_exemption_passes(self):
        """SPEC_AUTHORITY item with exemption_reason satisfies adoption compliance."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-SA-1",
                    "item_type": "SPEC_AUTHORITY",
                    "title": "Format backfill",
                    "status": "completed",
                    "exemption_reason": "SPEC_AUTHORITY lane — no product source changes"
                }
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is True

    def test_strict_fail_triggers_for_src_editing_track_without_exemption(self):
        """strict_fail triggers when src-editing-track items fail individually with no transcripts."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-X1",
                    "item_type": "PRODUCT_SOURCE",
                    "title": "Python FOSS work",
                    "product_track": "foss_python",
                },
            ]
        }
        result = validate_adoption(decl)
        assert result["compliant"] is False


class TestAntiSkipLaneLedgerDiscovery:
    """Lane ledger must be discoverable in evidence_root or via reports_created."""

    def test_ledger_in_evidence_root_found(self, tmp_path):
        """lane-execution-ledger.json in evidence_root satisfies missing_lane_ledger check."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        (evidence_root / "lane-execution-ledger.json").write_text('{"lanes": []}')
        result = detect_missing_lane_ledger(evidence_root, repo_root=tmp_path)
        assert result["is_violation"] is False

    def test_no_ledger_is_violation(self, tmp_path):
        """Missing lane ledger is a violation."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        result = detect_missing_lane_ledger(evidence_root, repo_root=tmp_path)
        assert result["is_violation"] is True

    def test_ledger_via_reports_created_found(self, tmp_path):
        """Ledger path in declaration.reports_created satisfies check."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        ledger_path = tmp_path / "reports" / "run-id" / "lane-ledger.json"
        ledger_path.parent.mkdir(parents=True)
        ledger_path.write_text('{"lanes": []}')
        declaration = {"run_id": "run-id", "reports_created": [str(ledger_path.relative_to(tmp_path))]}
        result = detect_missing_lane_ledger(evidence_root, declaration=declaration, repo_root=tmp_path)
        assert result["is_violation"] is False

    def test_current_sprint_ledger_present(self):
        """Current sprint lane ledger must exist in evidence_root."""
        run_id = "spec-authority-governance-closure-backfill-20260608-e382e5f"
        evidence_root = REPO_ROOT / ".local" / "evidences" / run_id
        if not evidence_root.exists():
            pytest.skip(f"Evidence root not found: {evidence_root}")
        result = detect_missing_lane_ledger(evidence_root, repo_root=REPO_ROOT)
        assert result["is_violation"] is False, (
            f"Lane ledger must exist in {evidence_root}. Found: {result['ledgers_found']}"
        )


_SPEC_CACHE = REPO_ROOT / ".local" / "spec-cache"


class TestPpmPromotion:
    """PPM must be at P4 after verified magic number facts from spec-index + crossref."""

    pytestmark = pytest.mark.skipif(
        not _SPEC_CACHE.is_dir(),
        reason="SAL spec-cache not present in this environment",
    )

    def test_ppm_reaches_p4(self):
        result = validate_format_authority("ppm")
        assert result["authority_level_int"] >= 4, (
            f"PPM should be P4+ after verified facts. Got P{result['authority_level_int']}."
        )

    def test_ppm_has_verified_facts(self):
        result = validate_format_authority("ppm")
        assert result["spec_state_summary"]["facts_verified"] >= 2, (
            "PPM must have at least 2 verified facts (P3 magic + P6 magic)"
        )

    def test_ppm_readiness_allowed(self):
        result = validate_format_authority("ppm")
        assert result["readiness_allowed"] is True, "PPM at P4 must be readiness_allowed"

    def test_ppm_p4_live(self):
        result = validate_format_authority("ppm")
        assert result["authority_level_int"] >= 4, (
            f"PPM should be P4+ (was promoted to P5 in Sprint 1). Got P{result['authority_level_int']}."
        )


class TestFormatAuthorityMatrixConsistency:
    """Format authority levels must be consistent with expected state."""

    pytestmark = pytest.mark.skipif(
        not _SPEC_CACHE.is_dir(),
        reason="SAL spec-cache not present in this environment",
    )

    def test_p6_formats(self):
        for fmt in ["fods", "zst"]:
            r = validate_format_authority(fmt)
            assert r["authority_level_int"] == 6, f"{fmt} must be P6"

    def test_p4_formats(self):
        for fmt in ["fodt", "pbm", "pgm", "ppm"]:
            r = validate_format_authority(fmt)
            assert r["authority_level_int"] >= 4, f"{fmt} must be P4+"

    def test_csv_below_p4(self):
        result = validate_format_authority("csv")
        assert result["authority_level_int"] <= 3, f"CSV must be P3 or below, got P{result['authority_level_int']}"

    def test_p0_p1_formats_not_readiness_allowed(self):
        for fmt in ["html", "gnumeric", "abw", "tsv"]:
            r = validate_format_authority(fmt)
            assert r["readiness_allowed"] is False, f"{fmt} at P{r['authority_level_int']} must not be readiness_allowed"
