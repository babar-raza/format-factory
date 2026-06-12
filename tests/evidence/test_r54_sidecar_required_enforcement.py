"""
test_r54_sidecar_required_enforcement.py — R54 Lane 2 tests.

Tests that sidecar proof enforcement is fail-closed when:
  - contract has sidecar_required: true and --sidecar-proof is missing
  - contract has final_proof_policy: external_sidecar and --sidecar-proof is missing
  - verdict contains SELF_VERIFYING/BASELINE_CLEAN tokens and sidecar is missing
  - sidecar bundle_filename does not match actual bundle filename
  - legacy contracts without sidecar_required still behave intentionally (optional)

R54 Sprint: FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import (
    check_sidecar_required,
    check_sidecar_filename_match,
    check_sidecar_proof,
)


# ---------------------------------------------------------------------------
# check_sidecar_required
# ---------------------------------------------------------------------------

class TestSidecarRequired:
    """Tests for check_sidecar_required (fail-closed enforcement)."""

    def test_no_sidecar_field_no_sidecar_passes(self):
        """Legacy contracts without sidecar_required default to optional (PASS)."""
        contract = {}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert errors == []

    def test_sidecar_required_false_no_sidecar_passes(self):
        """sidecar_required: false means optional — no sidecar is fine."""
        contract = {"sidecar_required": False}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert errors == []

    def test_sidecar_required_true_no_sidecar_fails(self):
        """sidecar_required: true without --sidecar-proof must FAIL."""
        contract = {"sidecar_required": True}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_sidecar_required_true_with_sidecar_passes(self):
        """sidecar_required: true with a sidecar path supplied — no enforcement error."""
        contract = {"sidecar_required": True}
        errors = check_sidecar_required(contract, sidecar_path="/some/sidecar.json")
        assert errors == []

    def test_final_proof_policy_external_sidecar_no_sidecar_fails(self):
        """final_proof_policy: external_sidecar implies required."""
        contract = {"final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_final_proof_policy_external_sidecar_with_sidecar_passes(self):
        """final_proof_policy: external_sidecar with sidecar path — passes enforcement."""
        contract = {"final_proof_policy": "external_sidecar"}
        errors = check_sidecar_required(contract, sidecar_path="/sidecar.json")
        assert errors == []

    def test_verdict_self_verifying_token_no_sidecar_fails(self):
        """Verdict with SELF_VERIFYING token implies sidecar required."""
        contract = {}
        errors = check_sidecar_required(
            contract, sidecar_path=None,
            verdict_content="R53_SELF_VERIFYING_BASELINE_001",
        )
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_verdict_baseline_clean_token_no_sidecar_fails(self):
        """Verdict with BASELINE_CLEAN token implies sidecar required."""
        contract = {}
        errors = check_sidecar_required(
            contract, sidecar_path=None,
            verdict_content="R53_STATE_VALIDATOR_BASELINE_CLEAN_001",
        )
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_verdict_installed_artifact_baseline_no_sidecar_fails(self):
        """Verdict with INSTALLED_ARTIFACT_BASELINE implies sidecar required."""
        contract = {}
        errors = check_sidecar_required(
            contract, sidecar_path=None,
            verdict_content="R52_INSTALLED_ARTIFACT_BASELINE_CLEAN",
        )
        assert len(errors) == 1
        assert "SIDECAR_REQUIRED" in errors[0]

    def test_ordinary_partial_verdict_no_sidecar_passes(self):
        """STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL — no sidecar required token."""
        contract = {}
        errors = check_sidecar_required(
            contract, sidecar_path=None,
            verdict_content="R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL",
        )
        assert errors == []


# ---------------------------------------------------------------------------
# check_sidecar_filename_match
# ---------------------------------------------------------------------------

class TestSidecarFilenameMatch:
    """Tests that sidecar bundle_filename matches actual bundle."""

    def _write_sidecar(self, bundle_filename: str, tmp_path: Path) -> Path:
        sidecar_data = {
            "sidecar_version": "1.0",
            "run_number": "R54",
            "bundle_filename": bundle_filename,
            "sha256": "a" * 64,
            "size_bytes": 1000,
            "entry_count": 10,
            "validation_result": "PASS",
        }
        sidecar_path = tmp_path / "test.sha256-proof.json"
        sidecar_path.write_text(json.dumps(sidecar_data), encoding="utf-8")
        return sidecar_path

    def test_matching_filename_passes(self, tmp_path):
        bundle_path = tmp_path / "r54-bundle.zip"
        bundle_path.write_bytes(b"dummy")
        sidecar_path = self._write_sidecar("r54-bundle.zip", tmp_path)
        errors = check_sidecar_filename_match(str(sidecar_path), str(bundle_path))
        assert errors == []

    def test_mismatched_filename_fails(self, tmp_path):
        bundle_path = tmp_path / "r54-bundle.zip"
        bundle_path.write_bytes(b"dummy")
        sidecar_path = self._write_sidecar("r53-bundle.zip", tmp_path)
        errors = check_sidecar_filename_match(str(sidecar_path), str(bundle_path))
        assert len(errors) == 1
        assert "SIDECAR_BUNDLE_FILENAME_MISMATCH" in errors[0]

    def test_missing_sidecar_fails(self, tmp_path):
        bundle_path = tmp_path / "r54-bundle.zip"
        bundle_path.write_bytes(b"dummy")
        errors = check_sidecar_filename_match(str(tmp_path / "nonexistent.json"), str(bundle_path))
        assert len(errors) == 1

    def test_empty_bundle_filename_field_passes(self, tmp_path):
        """Empty bundle_filename in sidecar is treated as not-set (no check)."""
        bundle_path = tmp_path / "r54-bundle.zip"
        bundle_path.write_bytes(b"dummy")
        sidecar_data = {"bundle_filename": "", "sha256": "a" * 64, "validation_result": "PASS"}
        sidecar_path = tmp_path / "test.sha256-proof.json"
        sidecar_path.write_text(json.dumps(sidecar_data), encoding="utf-8")
        errors = check_sidecar_filename_match(str(sidecar_path), str(bundle_path))
        assert errors == []


# ---------------------------------------------------------------------------
# check_sidecar_proof — result field
# ---------------------------------------------------------------------------

class TestSidecarResultField:
    """Tests that validation_result != PASS causes failure."""

    def _make_bundle(self, tmp_path: Path) -> Path:
        bundle = tmp_path / "bundle.zip"
        with zipfile.ZipFile(bundle, "w") as zf:
            zf.writestr("repo/state/current-state.md", "# state")
        return bundle

    def _make_sidecar(self, bundle: Path, tmp_path: Path, result: str) -> Path:
        import hashlib
        sha = hashlib.sha256(bundle.read_bytes()).hexdigest()
        with zipfile.ZipFile(bundle) as zf:
            entries = len(zf.namelist())
        sidecar_data = {
            "sha256": sha,
            "size_bytes": bundle.stat().st_size,
            "entry_count": entries,
            "validation_result": result,
        }
        sidecar_path = tmp_path / "bundle.sha256-proof.json"
        sidecar_path.write_text(json.dumps(sidecar_data), encoding="utf-8")
        return sidecar_path

    def test_result_fail_causes_error(self, tmp_path):
        bundle = self._make_bundle(tmp_path)
        sidecar = self._make_sidecar(bundle, tmp_path, "FAIL")
        errors = check_sidecar_proof(str(bundle), str(sidecar))
        assert any("SIDECAR_PROOF_RESULT_NOT_PASS" in e for e in errors)

    def test_result_pass_ok(self, tmp_path):
        bundle = self._make_bundle(tmp_path)
        sidecar = self._make_sidecar(bundle, tmp_path, "PASS")
        errors = check_sidecar_proof(str(bundle), str(sidecar))
        assert errors == []


# ---------------------------------------------------------------------------
# Legacy contract compatibility
# ---------------------------------------------------------------------------

class TestLegacyContractCompatibility:
    """Contracts without sidecar_required behave as before (optional)."""

    def test_no_sidecar_fields_optional_and_passes(self):
        contract = {"min_metadata_count": 30, "require_clean_git": True}
        errors = check_sidecar_required(contract, sidecar_path=None)
        assert errors == []

    def test_r53_contract_style_no_sidecar_required(self):
        """R53 contract style: sidecar_required not set — sidecar is optional."""
        contract = {
            "sprint_id": "FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001",
            "contract_id": "FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001",
            "min_metadata_count": 30,
            "require_clean_git": True,
        }
        errors = check_sidecar_required(contract, sidecar_path=None)
        # R53 contract does not set sidecar_required so it passes
        assert errors == []
