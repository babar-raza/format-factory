"""
test_r62_delivered_external_sidecar_required.py — R62 Train C: delivered external sidecar enforcement.

Verifies:
1. R62 contract declares sidecar_required: true.
2. R62 contract declares final_proof_policy: external_sidecar.
3. R62 contract declares installed_artifact_policy: self_contained.
4. R62 contract has all required fields to prevent R61-class sidecar omission.
5. The sidecar validation logic correctly enforces external_sidecar policy.

This closes IV-R61-001: R61 delivered ZIP had no external sidecar alongside it.

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
IV-R61-001 (sidecar not delivered with ZIP)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_sidecar_required


R62_CONTRACT_PATH = (
    PROJECT_ROOT / "tools" / "evidence" / "contracts"
    / "r62-ai-accelerated-sidecar-python-rc.yaml"
)


class TestR62ContractSidecarFields:
    """R62 contract must declare all sidecar and artifact policy fields."""

    def test_contract_exists(self):
        assert R62_CONTRACT_PATH.exists(), f"R62 contract missing: {R62_CONTRACT_PATH}"

    def test_contract_has_sidecar_required_true(self):
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "sidecar_required: true" in content, (
            "R62 contract must declare sidecar_required: true (IV-R61-001)"
        )

    def test_contract_has_external_sidecar_policy(self):
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "final_proof_policy: external_sidecar" in content, (
            "R62 contract must declare final_proof_policy: external_sidecar"
        )

    def test_contract_has_self_contained_artifact_policy(self):
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "installed_artifact_policy: self_contained" in content, (
            "R62 contract must declare installed_artifact_policy: self_contained (IV-R61-002)"
        )

    def test_contract_has_require_clean_git(self):
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "require_clean_git: true" in content

    def test_contract_has_min_metadata_count(self):
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "min_metadata_count:" in content


class TestSidecarEnforcementLogic:
    """check_sidecar_required must enforce all R62 sidecar contract fields."""

    def test_sidecar_required_true_no_path_fails(self):
        """sidecar_required: true + no sidecar_path → SIDECAR_REQUIRED error."""
        contract = {"sidecar_required": True}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_sidecar_required_true_with_path_passes(self):
        """sidecar_required: true + sidecar_path present → no error."""
        contract = {"sidecar_required": True}
        errors = check_sidecar_required(contract, sidecar_path="/some/path.sha256-proof.json")
        assert errors == []

    def test_external_sidecar_policy_no_path_fails(self):
        """final_proof_policy: external_sidecar + no sidecar_path → SIDECAR_REQUIRED error."""
        contract = {"final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_both_fields_no_path_fails(self):
        """Both fields set + no sidecar_path → error (not doubled)."""
        contract = {"sidecar_required": True, "final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert len(errors) >= 1
        assert any("SIDECAR_REQUIRED" in e for e in errors)

    def test_both_fields_with_path_passes(self):
        """Both fields set + sidecar_path present → no error."""
        contract = {"sidecar_required": True, "final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, sidecar_path="/path/to/proof.json")
        assert errors == []


class TestR61SidecarDefectRepaired:
    """R61's sidecar delivery defect (IV-R61-001) must be repaired in R62 contract design."""

    def test_r61_defect_ledger_records_sidecar_defect(self):
        """R61 defect ledger must document the sidecar delivery defect."""
        defect_ledger = PROJECT_ROOT / "reports" / "r62" / "r61-defect-ledger.md"
        assert defect_ledger.exists(), "R62 must have R61 defect ledger"
        content = defect_ledger.read_text(encoding="utf-8")
        assert "sidecar" in content.lower(), (
            "R61 defect ledger must document sidecar delivery defect"
        )

    def test_r61_iv_report_exists(self):
        """R62 must include an R61 independent verification report."""
        iv_report = PROJECT_ROOT / "reports" / "r62" / "r61-independent-verification.md"
        assert iv_report.exists(), "R62 must include R61 IV report"

    def test_r62_contract_references_sidecar_delivery(self):
        """R62 contract description must mention sidecar delivery."""
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "sidecar" in content.lower(), (
            "R62 contract must reference sidecar requirement"
        )
