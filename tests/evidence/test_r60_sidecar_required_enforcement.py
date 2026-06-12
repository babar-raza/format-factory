"""
test_r60_sidecar_required_enforcement.py — R60 Train B: Sidecar requirement enforcement tests.

Verifies that the R60 contract enforces sidecar_required: true correctly.
Repairs IV-R59-001, IV-R59-002, IV-R59-003.

R60 Sprint: FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

CONTRACT_PATH = PROJECT_ROOT / "tools" / "evidence" / "contracts" / "r60-current-head-rc-sidecar.yaml"


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_minimal_zip(tmp_path: Path, run_number: str = "R60") -> Path:
    zp = tmp_path / f"{run_number.lower()}-test-bundle.zip"
    with zipfile.ZipFile(zp, "w") as zf:
        zf.writestr("repo/state/current-state.md", "**Verdict:** R60_TEST_COMPLETE")
        zf.writestr("bundle-metadata/sprint-id.txt", run_number)
        zf.writestr("bundle-metadata/git-status-final.txt", "nothing to commit, working tree clean")
    return zp


def _make_sidecar(tmp_path: Path, bundle_path: Path, sha_override: str | None = None) -> Path:
    sha = sha_override if sha_override is not None else _compute_sha256(bundle_path)
    sidecar_data = {
        "sidecar_version": "1.0",
        "run_number": "R60",
        "bundle_filename": bundle_path.name,
        "sha256": sha,
        "size_bytes": bundle_path.stat().st_size,
        "entry_count": 3,
        "contract_path": "tools/evidence/contracts/r60-current-head-rc-sidecar.yaml",
        "validation_result": "PASS",
        "timestamp_utc": "2026-05-24T00:00:00+00:00",
    }
    sidecar_path = tmp_path / f"{bundle_path.name}.sha256-proof.json"
    sidecar_path.write_text(json.dumps(sidecar_data))
    return sidecar_path


class TestR60ContractSidecarRequired:
    """Verify the R60 contract requires sidecar."""

    def test_r60_contract_exists(self):
        assert CONTRACT_PATH.exists(), f"R60 contract not found: {CONTRACT_PATH}"

    def test_r60_contract_sidecar_required_true(self):
        """R60 contract must specify sidecar_required: true."""
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        assert "sidecar_required: true" in text, (
            "R60 contract must have sidecar_required: true"
        )

    def test_r60_contract_final_proof_policy_external_sidecar(self):
        """R60 contract must use final_proof_policy: external_sidecar."""
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        assert "final_proof_policy: external_sidecar" in text

    def test_r60_contract_require_clean_git_true(self):
        """R60 contract must require clean git."""
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        assert "require_clean_git: true" in text

    def test_r60_contract_run_number_is_r60(self):
        """Contract must identify as R60."""
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        assert "run_number: R60" in text


class TestR60SidecarValidation:
    """Sidecar validation is enforced for R60 bundles."""

    def test_correct_sidecar_accepted(self, tmp_path):
        """Validator accepts a correct matching sidecar."""
        bundle = _make_minimal_zip(tmp_path)
        sidecar = _make_sidecar(tmp_path, bundle)
        from tools.evidence.validate_evidence_bundle import check_sidecar_proof
        errors = check_sidecar_proof(str(bundle), str(sidecar))
        sha_errors = [e for e in errors if "SHA_MISMATCH" in e]
        assert sha_errors == [], f"Correct sidecar should not produce SHA errors: {sha_errors}"

    def test_missing_sidecar_would_trigger_sidecar_required(self, tmp_path):
        """Verify that check_sidecar_required detects missing sidecar."""
        bundle = _make_minimal_zip(tmp_path)
        # No sidecar file — check the sidecar_required function
        from tools.evidence.validate_evidence_bundle import check_sidecar_required
        contract = {"sidecar_required": True}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert any("SIDECAR_REQUIRED" in e for e in errors), (
            f"Missing sidecar must trigger SIDECAR_REQUIRED. Got: {errors}"
        )

    def test_wrong_sha_sidecar_rejected(self, tmp_path):
        """Validator rejects sidecar with wrong SHA."""
        bundle = _make_minimal_zip(tmp_path)
        sidecar = _make_sidecar(tmp_path, bundle, sha_override="a" * 64)
        from tools.evidence.validate_evidence_bundle import check_sidecar_proof
        errors = check_sidecar_proof(str(bundle), str(sidecar))
        assert any("SIDECAR_PROOF_SHA_MISMATCH" in e for e in errors)

    def test_sidecar_outside_zip(self, tmp_path):
        """Sidecar must be a separate file, not inside the ZIP."""
        bundle = _make_minimal_zip(tmp_path)
        sidecar = _make_sidecar(tmp_path, bundle)
        # Sidecar must be a sibling of the ZIP, not inside it
        with zipfile.ZipFile(bundle) as zf:
            names = zf.namelist()
        sidecar_in_zip = [n for n in names if "sha256-proof" in n]
        assert sidecar_in_zip == [], "Sidecar must NOT be inside the ZIP"
        assert sidecar.parent == bundle.parent, "Sidecar must be in same directory as ZIP"

    def test_sidecar_not_inside_zip_validator_function(self, tmp_path):
        """check_repo_sidecar_not_inside_zip accepts bundle without embedded sidecar."""
        bundle = _make_minimal_zip(tmp_path)
        from tools.evidence.validate_evidence_bundle import check_repo_sidecar_not_inside_zip
        with zipfile.ZipFile(bundle) as zf:
            errors = check_repo_sidecar_not_inside_zip(zf, str(bundle))
        assert errors == [], f"Clean bundle should not have sidecar-inside-zip errors: {errors}"

    def test_sidecar_validation_result_must_be_pass(self, tmp_path):
        """Validator rejects sidecar where validation_result != PASS."""
        bundle = _make_minimal_zip(tmp_path)
        sha = _compute_sha256(bundle)
        sidecar_data = {
            "sidecar_version": "1.0",
            "run_number": "R60",
            "bundle_filename": bundle.name,
            "sha256": sha,
            "size_bytes": bundle.stat().st_size,
            "entry_count": 3,
            "contract_path": "test.yaml",
            "validation_result": "FAIL",  # MUST be PASS
            "timestamp_utc": "2026-05-24T00:00:00+00:00",
        }
        sidecar_path = tmp_path / f"{bundle.name}.sha256-proof.json"
        sidecar_path.write_text(json.dumps(sidecar_data))
        from tools.evidence.validate_evidence_bundle import check_sidecar_proof
        errors = check_sidecar_proof(str(bundle), str(sidecar_path))
        assert any("SIDECAR" in e for e in errors), (
            f"FAIL sidecar should be rejected. Got: {errors}"
        )

    def test_sidecar_sha256_is_64_chars(self, tmp_path):
        """SHA-256 in sidecar must be exactly 64 hexadecimal characters."""
        bundle = _make_minimal_zip(tmp_path)
        sidecar = _make_sidecar(tmp_path, bundle)
        data = json.loads(sidecar.read_text())
        sha = data.get("sha256") or data.get("bundle_sha256", "")
        assert len(sha) == 64, f"SHA-256 must be 64 chars, got {len(sha)}"
        assert all(c in "0123456789abcdef" for c in sha), "SHA-256 must be lowercase hex"

    def test_sidecar_required_false_allows_no_sidecar(self, tmp_path):
        """When sidecar_required is false, no sidecar is acceptable."""
        bundle = _make_minimal_zip(tmp_path)
        from tools.evidence.validate_evidence_bundle import check_sidecar_required
        contract = {"sidecar_required": False}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert errors == [], f"sidecar_required=False should allow no sidecar: {errors}"
