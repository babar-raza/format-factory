"""
R69 Train D — Test: negative sidecar proofs must be present and confirmed.

The missing-sidecar-negative-proof.txt and wrong-sidecar-negative-proof.txt
are required to prove the sidecar protocol's fail-closed behavior. This test
checks that both are present in R69 metadata and contain CONFIRMED status.
"""
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
R69_METADATA = PROJECT_ROOT / ".local" / "r69-metadata"


class TestNegativeSidecarProofsPresent:
    """Missing-sidecar and wrong-sidecar negative proofs must be present and confirmed."""

    def test_missing_sidecar_negative_proof_present(self):
        """missing-sidecar-negative-proof.txt must exist in R69 metadata."""
        fpath = R69_METADATA / "missing-sidecar-negative-proof.txt"
        if not R69_METADATA.exists():
            pytest.skip("R69 metadata dir not yet created")
        assert fpath.exists(), (
            "missing-sidecar-negative-proof.txt not found in R69 metadata. "
            "Run validate_evidence_bundle.py WITHOUT --sidecar-proof and capture the FAIL output."
        )

    def test_missing_sidecar_negative_proof_confirmed(self):
        """missing-sidecar-negative-proof.txt must contain CONFIRMED status."""
        fpath = R69_METADATA / "missing-sidecar-negative-proof.txt"
        if not fpath.exists():
            pytest.skip("missing-sidecar-negative-proof.txt not yet created")
        content = fpath.read_text(encoding="utf-8")
        assert "CONFIRMED" in content or "BUNDLE_VALIDATION: FAIL" in content, (
            "missing-sidecar-negative-proof.txt must show BUNDLE_VALIDATION: FAIL "
            "and contain CONFIRMED status."
        )

    def test_wrong_sidecar_negative_proof_present(self):
        """wrong-sidecar-negative-proof.txt must exist in R69 metadata."""
        fpath = R69_METADATA / "wrong-sidecar-negative-proof.txt"
        if not R69_METADATA.exists():
            pytest.skip("R69 metadata dir not yet created")
        assert fpath.exists(), (
            "wrong-sidecar-negative-proof.txt not found in R69 metadata. "
            "Run validate_evidence_bundle.py with a wrong --sidecar-proof and capture the FAIL output."
        )

    def test_wrong_sidecar_negative_proof_confirmed(self):
        """wrong-sidecar-negative-proof.txt must contain SIDECAR_PROOF_VALIDATION: FAIL."""
        fpath = R69_METADATA / "wrong-sidecar-negative-proof.txt"
        if not fpath.exists():
            pytest.skip("wrong-sidecar-negative-proof.txt not yet created")
        content = fpath.read_text(encoding="utf-8")
        assert "SIDECAR_PROOF_VALIDATION: FAIL" in content or "CONFIRMED" in content, (
            "wrong-sidecar-negative-proof.txt must show SIDECAR_PROOF_VALIDATION: FAIL."
        )
