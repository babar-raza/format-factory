"""
R69 Train D — Test: inner evidence ZIP and external sidecar must be consistent.

Covers IV-R69-002/003: R68's metadata had stale SHA 10c57c6f (from aborted first
pass 2 build) but the actual final pass 2 ZIP had SHA 209017ee. This test verifies
that the sidecar's claimed SHA matches the actual inner ZIP file on disk.
"""
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
R69_LOCAL = PROJECT_ROOT / ".local"


class TestInnerZipSidecarConsistency:
    """Inner ZIP and external sidecar must have consistent SHA-256 values."""

    def test_r69_sidecar_sha_matches_inner_zip(self):
        """Sidecar's sha256 must match the actual inner ZIP file on disk."""
        sidecar_path = R69_LOCAL / "r69-pass2-final.sha256-proof.json"
        inner_zip = R69_LOCAL / "r69-pass2-final.zip"
        if not sidecar_path.exists() or not inner_zip.exists():
            pytest.skip("R69 pass 2 artifacts not yet built")
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        actual_sha = hashlib.sha256(inner_zip.read_bytes()).hexdigest()
        sidecar_sha = sidecar.get("sha256", "")
        assert actual_sha == sidecar_sha, (
            f"Sidecar SHA mismatch: actual inner ZIP SHA={actual_sha}, "
            f"sidecar claims={sidecar_sha}. "
            "This indicates a stale sidecar was not regenerated after bundle rebuild."
        )

    def test_r69_sidecar_not_embedded_in_inner_zip(self):
        """The external sidecar must NOT be embedded inside the inner evidence ZIP."""
        inner_zip = R69_LOCAL / "r69-pass2-final.zip"
        if not inner_zip.exists():
            pytest.skip("R69 pass 2 ZIP not yet built")
        with zipfile.ZipFile(inner_zip) as z:
            names = z.namelist()
        sidecar_in_bundle = [n for n in names if "sha256-proof.json" in n]
        assert not sidecar_in_bundle, (
            f"Sidecar file found inside inner ZIP: {sidecar_in_bundle}. "
            "The external sidecar must be outside the evidence ZIP."
        )

    def test_r68_had_stale_sha_in_proof(self):
        """Verify R68 defect: final-bundle-validation-proof.txt had stale Pass 2 SHA."""
        r68_proof = PROJECT_ROOT / ".local" / "r68-metadata" / "final-bundle-validation-proof.txt"
        if not r68_proof.exists():
            pytest.skip("R68 metadata not found")
        content = r68_proof.read_text(encoding="utf-8")
        # R68 proof should have the old SHA 10c57c6f (not the final 209017ee)
        assert "10c57c6f" in content, (
            "Historical test: R68 final-bundle-validation-proof.txt should have "
            "recorded stale SHA 10c57c6f (IV-R69-002). This documents the repaired defect."
        )

    def test_r69_sidecar_validation_result_pass(self):
        """R69 sidecar must record validation_result: PASS."""
        sidecar_path = R69_LOCAL / "r69-pass2-final.sha256-proof.json"
        if not sidecar_path.exists():
            pytest.skip("R69 sidecar not yet built")
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert sidecar.get("validation_result") == "PASS", (
            f"Sidecar validation_result must be PASS, got: {sidecar.get('validation_result')}"
        )
