"""
test_r63_delivered_external_sidecar_required.py — R63 Train C: delivered external sidecar enforcement.

Verifies:
1. R63 contract declares sidecar_required: true.
2. R63 contract declares final_proof_policy: external_sidecar.
3. R63 contract declares installed_artifact_policy: self_contained.
4. R63 contract has all required fields to prevent R62-class sidecar omission.
5. The sidecar validation logic correctly enforces external_sidecar policy.
6. R63 contract requires sidecar test files (closing IV-R62-001 recurrence prevention).

This closes IV-R62-001 (sidecar not committed/delivered) by enforcing at contract level.

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
IV-R62-001 (sidecar not delivered with R62 ZIP)
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_sidecar_required


R63_CONTRACT_PATH = (
    PROJECT_ROOT / "tools" / "evidence" / "contracts"
    / "r63-ai-assisted-rc-closure-and-workahead.yaml"
)


class TestR63ContractSidecarFields:
    """R63 contract must declare all sidecar and artifact policy fields."""

    def test_contract_exists(self):
        assert R63_CONTRACT_PATH.exists(), f"R63 contract missing: {R63_CONTRACT_PATH}"

    def test_contract_has_sidecar_required_true(self):
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "sidecar_required: true" in content, (
            "R63 contract must declare sidecar_required: true (IV-R62-001 prevention)"
        )

    def test_contract_has_external_sidecar_policy(self):
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "final_proof_policy: external_sidecar" in content, (
            "R63 contract must declare final_proof_policy: external_sidecar"
        )

    def test_contract_has_self_contained_artifact_policy(self):
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "installed_artifact_policy: self_contained" in content, (
            "R63 contract must declare installed_artifact_policy: self_contained"
        )

    def test_contract_has_require_clean_git(self):
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "require_clean_git: true" in content, (
            "R63 contract must require clean git before bundle build"
        )

    def test_contract_requires_sidecar_test_files(self):
        """R63 contract must require sidecar test files (closing IV-R62-004 recurrence)."""
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "test_r63_delivered_external_sidecar_required.py" in content
        assert "test_r63_final_response_sidecar_path_exists.py" in content
        assert "test_r63_sidecar_not_inside_zip.py" in content

    def test_contract_has_final_verdict_required(self):
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "reports/r63/final-verdict.md" in content, (
            "R63 contract must require final-verdict.md"
        )


class TestR63SidecarValidationLogic:
    """The sidecar enforcement logic must correctly reject missing sidecars."""

    def test_check_sidecar_required_function_exists(self):
        """check_sidecar_required must be importable from validate_evidence_bundle."""
        assert callable(check_sidecar_required), (
            "check_sidecar_required must be a callable function"
        )

    def test_check_sidecar_required_rejects_none_sidecar_path(self):
        """check_sidecar_required returns errors when sidecar_path is None and required.

        The function checks if --sidecar-proof was supplied (None = not supplied),
        not whether the file exists on disk.
        """
        contract = {"sidecar_required": True, "final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, None, "")
        assert len(errors) > 0, (
            "check_sidecar_required must return errors when sidecar_path is None and required"
        )

    def test_check_sidecar_not_required_passes_with_none_path(self):
        """When sidecar_required is false, check must pass even with None sidecar_path."""
        contract = {"sidecar_required": False}
        errors = check_sidecar_required(contract, None, "")
        assert errors == [], (
            f"check_sidecar_required must pass when not required; got: {errors}"
        )

    def test_check_sidecar_rejects_self_verifying_verdict_without_sidecar(self):
        """SELF_VERIFYING verdict with no sidecar path must fail validation."""
        contract = {"sidecar_required": False}
        verdict_content = "VERDICT: R63_SELF_VERIFYING_PASS"
        errors = check_sidecar_required(contract, None, verdict_content)
        assert len(errors) > 0, (
            "SELF_VERIFYING verdict without sidecar must fail validation"
        )


class TestR62SidecarPolicyNotRepeated:
    """Confirm IV-R62-001 pattern is not repeated in R63 contract."""

    def test_r63_contract_not_missing_sidecar_fields(self):
        """R63 contract must have all fields that R61 (pre-sidecar) was missing."""
        content = R63_CONTRACT_PATH.read_text(encoding="utf-8")
        missing = []
        for field in ["sidecar_required", "final_proof_policy", "installed_artifact_policy"]:
            if field not in content:
                missing.append(field)
        assert not missing, (
            f"R63 contract is missing sidecar-related fields: {missing}\n"
            "This would repeat IV-R62-001 (R61 had no sidecar policy)."
        )

    def test_r62_contract_also_has_sidecar_required(self):
        """R62 contract must also have sidecar_required: true (historical record)."""
        r62_contract = (
            PROJECT_ROOT / "tools" / "evidence" / "contracts"
            / "r62-ai-accelerated-sidecar-python-rc.yaml"
        )
        assert r62_contract.exists()
        content = r62_contract.read_text(encoding="utf-8")
        assert "sidecar_required: true" in content, (
            "R62 contract must have sidecar_required: true"
        )
