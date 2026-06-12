"""
test_r57_sidecar_required_top_level.py — R57 Train B: sidecar_required contract enforcement.

Verifies:
1. When contract has sidecar_required: true, validation fails without --sidecar-proof.
2. When contract has final_proof_policy: external_sidecar, sidecar is also required.
3. When both fields are present and sidecar is supplied, no error is raised.
4. A bundle built without sidecar must NOT pass if contract requires one.

This closes IV-R56-001/002: R56 contract lacked sidecar_required, so no enforcement.

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
IV-R56-001, IV-R56-002
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_sidecar_required


class TestSidecarRequiredContractField:
    """check_sidecar_required must enforce sidecar_required: true in contract."""

    def test_no_sidecar_path_when_required_fails(self):
        """Contract sidecar_required: true + no sidecar_path → error."""
        contract = {"sidecar_required": True}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_sidecar_path_supplied_when_required_passes(self):
        """Contract sidecar_required: true + sidecar_path supplied → no error."""
        contract = {"sidecar_required": True}
        errors = check_sidecar_required(contract, sidecar_path="/some/path.sha256-proof.json")
        assert errors == []

    def test_not_required_without_field_passes(self):
        """Contract without sidecar_required field and no sidecar → no error."""
        contract = {}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert errors == []

    def test_sidecar_required_false_no_sidecar_passes(self):
        """Contract sidecar_required: false + no sidecar → no error."""
        contract = {"sidecar_required": False}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert errors == []


class TestFinalProofPolicyExternalSidecar:
    """final_proof_policy: external_sidecar must also require a sidecar."""

    def test_external_sidecar_policy_no_sidecar_fails(self):
        """final_proof_policy: external_sidecar + no sidecar_path → error."""
        contract = {"final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_external_sidecar_policy_with_sidecar_passes(self):
        """final_proof_policy: external_sidecar + sidecar_path → no error."""
        contract = {"final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, sidecar_path="/path/to/sidecar.json")
        assert errors == []

    def test_internal_policy_no_sidecar_passes(self):
        """final_proof_policy: internal + no sidecar_path → no error."""
        contract = {"final_proof_policy": "internal"}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert errors == []


class TestR57ContractHasSidecarFields:
    """The R57 contract file must contain sidecar_required: true and final_proof_policy."""

    R57_CONTRACT = (
        PROJECT_ROOT / "tools" / "evidence" / "contracts"
        / "r57-self-verifying-rc-replay.yaml"
    )

    def test_contract_file_exists(self):
        assert self.R57_CONTRACT.exists(), f"R57 contract missing: {self.R57_CONTRACT}"

    def test_contract_has_sidecar_required(self):
        content = self.R57_CONTRACT.read_text(encoding="utf-8")
        assert "sidecar_required: true" in content, (
            "R57 contract must declare sidecar_required: true (IV-R56-002)"
        )

    def test_contract_has_final_proof_policy(self):
        content = self.R57_CONTRACT.read_text(encoding="utf-8")
        assert "final_proof_policy: external_sidecar" in content, (
            "R57 contract must declare final_proof_policy: external_sidecar (IV-R56-002)"
        )

    def test_contract_has_require_clean_git(self):
        content = self.R57_CONTRACT.read_text(encoding="utf-8")
        assert "require_clean_git: true" in content
