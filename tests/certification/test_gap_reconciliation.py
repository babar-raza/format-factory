"""Tests for gap_reconciler.py — TC-005 (precious-wandering-lighthouse, 2026-07-13)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "certification"))

from gap_reconciler import match_finding_to_gap, reconcile


def _make_ledger_gap(gap_id="GAP-CSV-FOSS-STUBS-001", fmt="csv",
                     capability="stub_free_implementation", gap_type="material_stub"):
    return {
        "gap_id": gap_id,
        "format": fmt,
        "capability_name": capability,
        "gap_type": gap_type,
        "status": "open",
    }


class TestMatchFindingToGap:
    """match_finding_to_gap returns correct action for known and unknown findings."""

    def test_known_finding_matches_existing_gap(self):
        finding = {
            "finding_id": "CERT-TEST-001",
            "format_id": "csv",
            "certification_dimension": "stubs",
            "stable_semantic_key": "stub_free",
            "gap_type": "material_stub",
            "is_product_gap": True,
        }
        gaps = [_make_ledger_gap()]
        gap_id, action = match_finding_to_gap(finding, gaps)
        assert action == "LINK_EXISTING", (
            f"Expected LINK_EXISTING for matching format+semantic_key; got {action}"
        )
        assert gap_id == "GAP-CSV-FOSS-STUBS-001"

    def test_unknown_finding_returns_create_new(self):
        finding = {
            "finding_id": "CERT-UNKNOWN-001",
            "format_id": "fods",
            "certification_dimension": "roundtrip",
            "stable_semantic_key": "lossless_roundtrip",
            "gap_type": "missing_roundtrip",
            "is_product_gap": True,
        }
        gaps = [_make_ledger_gap()]  # CSV gap, not FODS
        gap_id, action = match_finding_to_gap(finding, gaps)
        assert action == "CREATE_NEW", (
            f"Expected CREATE_NEW for finding with no matching gap; got {action}"
        )
        assert gap_id is None

    def test_non_product_gap_returns_invalid(self):
        finding = {
            "finding_id": "CERT-STRUCT-001",
            "format_id": "ALL",
            "certification_dimension": "dashboard",
            "stable_semantic_key": "missing_evidence_defaults_to_pass",
            "is_product_gap": False,
        }
        gaps = [_make_ledger_gap()]
        gap_id, action = match_finding_to_gap(finding, gaps)
        assert action == "INVALID", (
            f"Expected INVALID for is_product_gap=False; got {action}"
        )
        assert gap_id is None

    def test_empty_ledger_returns_create_new(self):
        finding = {
            "finding_id": "CERT-EMPTY-001",
            "format_id": "tsv",
            "certification_dimension": "stubs",
            "stable_semantic_key": "stub_free",
            "gap_type": "material_stub",
            "is_product_gap": True,
        }
        gap_id, action = match_finding_to_gap(finding, [])
        assert action == "CREATE_NEW"
        assert gap_id is None


class TestReconcile:
    """reconcile() produces correct output file with no duplicate gaps."""

    def test_reconcile_produces_output_file(self, tmp_path):
        findings = {
            "schema_version": "1.0",
            "mission_id": "TEST-MISSION",
            "findings": [
                {
                    "finding_id": "CERT-T-001",
                    "format_id": "ALL",
                    "certification_dimension": "dashboard",
                    "stable_semantic_key": "missing_evidence",
                    "description": "Missing evidence test",
                    "is_product_gap": False,
                }
            ],
        }
        ledger = {"schema_version": "1.0", "gaps": []}

        findings_path = tmp_path / "findings.json"
        findings_path.write_text(json.dumps(findings))
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(ledger))
        output_path = tmp_path / "reconciliation-map.yaml"

        result = reconcile(findings_path, ledger_path, output_path)
        assert output_path.exists(), "Reconciler must write output file"
        assert result["total_findings"] == 1
        assert result["invalid"] == 1  # is_product_gap=False

    def test_reconcile_idempotent_no_duplicate_gaps(self, tmp_path):
        """Running reconciler twice must not create duplicate gap entries."""
        findings = {
            "schema_version": "1.0",
            "mission_id": "TEST-MISSION",
            "findings": [
                {
                    "finding_id": "CERT-T-002",
                    "format_id": "csv",
                    "certification_dimension": "stubs",
                    "stable_semantic_key": "stub_free",
                    "gap_type": "material_stub",
                    "description": "Stub test",
                    "is_product_gap": True,
                }
            ],
        }
        ledger = {"schema_version": "1.0", "gaps": []}

        findings_path = tmp_path / "findings.json"
        findings_path.write_text(json.dumps(findings))
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(ledger))
        output_path = tmp_path / "reconciliation-map.yaml"

        result1 = reconcile(findings_path, ledger_path, output_path)
        result2 = reconcile(findings_path, ledger_path, output_path)

        assert result1["create_new"] == result2["create_new"], (
            "Reconciler must be idempotent — running twice must produce same result"
        )

    def test_reconcile_against_actual_findings(self):
        """Running against normalized-findings.yaml produces CLEAN verdict."""
        findings_path = REPO_ROOT / "reports" / "certification-integration" / "normalized-findings.yaml"
        ledger_path = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
        output_path = REPO_ROOT / "reports" / "certification-integration" / "gap-reconciliation-map-v2.yaml"

        if not findings_path.exists() or not ledger_path.exists():
            pytest.skip("normalized-findings.yaml or gap-ledger.json not present")

        result = reconcile(findings_path, ledger_path, output_path)
        assert output_path.exists()
        # All 5 structural findings are is_product_gap=false → INVALID → CLEAN
        assert result["reconciliation_verdict"] == "CLEAN", (
            f"Structural certification findings must yield CLEAN verdict; "
            f"got {result['reconciliation_verdict']}. "
            f"CREATE_NEW={result['create_new']} (unexpected product gaps)"
        )
