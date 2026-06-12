"""
test_r74_requires_real_negative_proof_logs.py

R74 Train B: Validator must warn when negative proof files lack actual command evidence.
Real negative proofs must include validate_evidence_bundle invocation, exit code, and
a FAIL marker.

Sprint: FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_negative_proof_quality


class TestNegativeProofQuality:
    """R74: negative proof files must contain actual command evidence."""

    def test_stub_missing_sidecar_proof_gets_warning(self):
        metadata = {
            "missing-sidecar-negative-proof.txt": (
                "R73 Missing Sidecar Negative Proof\n"
                "Test: test_r73_rejects_missing_physical_sidecar.py\n"
                "Result: ALL PASS (4/4)\n"
                "Proof: If delivery package lacks a sidecar, validation fails.\n"
                "MISSING_SIDECAR_NEGATIVE_PROOF: PASS\n"
            )
        }
        warnings = check_negative_proof_quality(metadata)
        assert len(warnings) > 0, "Stub proof without actual command must generate warning"
        assert any("missing-sidecar" in w for w in warnings)

    def test_real_missing_sidecar_proof_passes(self):
        metadata = {
            "missing-sidecar-negative-proof.txt": (
                "Command: python tools/evidence/validate_evidence_bundle.py "
                "--bundle .local/r74-pass2-final.zip "
                "--contract tools/evidence/contracts/r74-...yaml "
                "--sidecar-proof /dev/null\n"
                "exit code: 1\n"
                "Output: SIDECAR_PROOF_VALIDATION: FAIL\n"
                "MISSING_SIDECAR_NEGATIVE_PROOF: CONFIRMED\n"
            )
        }
        warnings = check_negative_proof_quality(metadata)
        assert len(warnings) == 0, f"Real proof must not generate warning: {warnings}"

    def test_stub_wrong_sidecar_proof_gets_warning(self):
        metadata = {
            "wrong-sidecar-negative-proof.txt": (
                "R73 Wrong Sidecar Negative Proof\n"
                "Test: test_r70_validator_rejects_wrong_sidecar_file_sha.py\n"
                "WRONG_SIDECAR_NEGATIVE_PROOF: PASS\n"
            )
        }
        warnings = check_negative_proof_quality(metadata)
        assert len(warnings) > 0, "Stub wrong-sidecar proof must generate warning"
        assert any("wrong-sidecar" in w for w in warnings)

    def test_real_wrong_sidecar_proof_passes(self):
        metadata = {
            "wrong-sidecar-negative-proof.txt": (
                "Command: python tools/evidence/validate_evidence_bundle.py "
                "--bundle .local/r74-pass2-final.zip "
                "--sidecar-proof .local/r73-pass2-final.sha256-proof.json\n"
                "exit code: 1\n"
                "SIDECAR_PROOF_VALIDATION: FAIL (SHA mismatch)\n"
                "WRONG_SIDECAR_NEGATIVE_PROOF: CONFIRMED\n"
            )
        }
        warnings = check_negative_proof_quality(metadata)
        assert len(warnings) == 0, f"Real wrong-sidecar proof must not warn: {warnings}"

    def test_no_negative_proof_files_no_warning(self):
        """If negative proof files are absent, no warning (absence handled separately)."""
        metadata = {"python-tests-summary.txt": "6120 passed\n"}
        warnings = check_negative_proof_quality(metadata)
        assert len(warnings) == 0

    def test_inner_zip_only_proof_stub_warned(self):
        metadata = {
            "inner-zip-only-negative-proof.txt": (
                "Inner ZIP only: validation rejects.\n"
                "INNER_ZIP_ONLY_NEGATIVE_PROOF: PASS\n"
            )
        }
        warnings = check_negative_proof_quality(metadata)
        assert len(warnings) > 0, "Stub inner-zip-only proof must generate warning"

    def test_inner_zip_only_real_proof_passes(self):
        metadata = {
            "inner-zip-only-negative-proof.txt": (
                "Command: python tools/evidence/validate_evidence_bundle.py "
                "--bundle .local/r74-delivery-package.zip\n"
                "exit code: 1\n"
                "BUNDLE_VALIDATION: FAIL (inner ZIP only delivery rejected)\n"
                "INNER_ZIP_ONLY_NEGATIVE_PROOF: CONFIRMED\n"
            )
        }
        warnings = check_negative_proof_quality(metadata)
        assert len(warnings) == 0
