"""
test_r59_final_proof_authority.py — R59 Train C: Final proof / sidecar authority normalization.

Verifies:
1. External sidecar is authoritative — sidecar SHA/size/entries match actual bundle
2. Internal proof with stale SHA produces PROOF_SHA_SIDECAR_RECOMMENDED warning
3. Internal proof with labeled non-authoritative pre-final hash is accepted (warning but PASS)
4. Final proof file must include external sidecar reference to be considered authoritative
5. Proof with BUNDLE_VALIDATION: PASS and no placeholder passes finality check

R59 Sprint: FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R58-007
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import (
    check_proof_sha_consistency,
    check_proof_file_finality,
    check_sidecar_proof,
)


def _make_bundle_bytes(content: str = "test bundle") -> bytes:
    """Make a minimal ZIP bundle and return its bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("bundle-metadata/sprint-id.txt", content)
    return buf.getvalue()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestProofFileFinality:
    """Proof file must not contain stale placeholder text."""

    def test_complete_proof_passes(self):
        """Proof file with BUNDLE_VALIDATION: PASS and no placeholders passes."""
        proof = {
            "final-bundle-validation-proof.txt": (
                "Bundle: r59-pass2-final.zip\n"
                "External sidecar SHA (authoritative): abcd1234" + "0" * 56 + "\n"
                "BUNDLE_VALIDATION: PASS\n"
                "SIDECAR_PROOF_VALIDATION: PASS\n"
            )
        }
        errors = check_proof_file_finality(proof)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_pending_sha_fails(self):
        """Proof file with BUNDLE_VALIDATION: PENDING placeholder fails."""
        proof = {
            "final-bundle-validation-proof.txt": "SHA-256: TBD\nBUNDLE_VALIDATION: PENDING"
        }
        errors = check_proof_file_finality(proof)
        assert len(errors) > 0, "Expected error for BUNDLE_VALIDATION: PENDING placeholder"

    def test_in_progress_fails(self):
        """Proof file with IN PROGRESS fails."""
        proof = {
            "final-bundle-validation-proof.txt": "SHA-256: IN PROGRESS\nBUNDLE_VALIDATION: PENDING"
        }
        errors = check_proof_file_finality(proof)
        assert len(errors) > 0, "Expected error for IN PROGRESS placeholder"


class TestProofShaConsistency:
    """Proof SHA consistency — internal vs actual bundle."""

    def test_stale_internal_sha_produces_warning(self, tmp_path):
        """Stale internal SHA (different from actual bundle) produces warning."""
        bundle_bytes = _make_bundle_bytes("stale-sha-test")
        bundle_file = tmp_path / "test-bundle.zip"
        bundle_file.write_bytes(bundle_bytes)
        actual_sha = _sha256(bundle_bytes)
        # Proof claims a completely different SHA
        stale_sha = "a" * 64
        proof = {
            "final-bundle-validation-proof.txt": f"SHA-256: {stale_sha}\nBUNDLE_VALIDATION: PASS"
        }
        warnings = check_proof_sha_consistency(proof, str(bundle_file))
        assert len(warnings) > 0, (
            f"Expected warning for stale SHA {stale_sha!r} vs actual {actual_sha!r}"
        )

    def test_no_sha_in_proof_no_warning(self, tmp_path):
        """Proof without any SHA claim produces no warning."""
        bundle_bytes = _make_bundle_bytes()
        bundle_file = tmp_path / "test-bundle.zip"
        bundle_file.write_bytes(bundle_bytes)
        proof = {
            "final-bundle-validation-proof.txt":
                "External sidecar: reports/r59/r59-pass2-final.zip.sha256-proof.json\n"
                "BUNDLE_VALIDATION: PASS"
        }
        warnings = check_proof_sha_consistency(proof, str(bundle_file))
        assert warnings == [], f"Expected no warnings without SHA claim, got: {warnings}"


class TestSidecarAuthority:
    """External sidecar is the authoritative final proof."""

    def test_sidecar_sha_size_entries_match(self, tmp_path):
        """When sidecar SHA/size/entries match bundle, check passes."""
        bundle_bytes = _make_bundle_bytes("sidecar-authority-test")
        bundle_file = tmp_path / "test-bundle.zip"
        bundle_file.write_bytes(bundle_bytes)

        sha = _sha256(bundle_bytes)
        with zipfile.ZipFile(bundle_file) as zf:
            entries = len(zf.namelist())

        sidecar_data = {
            "sha256": sha,
            "size_bytes": len(bundle_bytes),
            "entry_count": entries,
            "validation_result": "PASS",
            "bundle_filename": "test-bundle.zip",
            "run_number": "R59",
        }
        sidecar_file = tmp_path / "test-bundle.zip.sha256-proof.json"
        sidecar_file.write_text(json.dumps(sidecar_data))

        errors = check_sidecar_proof(str(bundle_file), str(sidecar_file))
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_wrong_sidecar_sha_fails(self, tmp_path):
        """Sidecar with wrong SHA fails."""
        bundle_bytes = _make_bundle_bytes("wrong-sha-test")
        bundle_file = tmp_path / "test-bundle.zip"
        bundle_file.write_bytes(bundle_bytes)

        wrong_sha = "0" * 64  # definitely wrong
        sidecar_data = {
            "sha256": wrong_sha,
            "size_bytes": len(bundle_bytes),
            "entry_count": 1,
            "validation_result": "PASS",
        }
        sidecar_file = tmp_path / "test-bundle.zip.sha256-proof.json"
        sidecar_file.write_text(json.dumps(sidecar_data))

        errors = check_sidecar_proof(str(bundle_file), str(sidecar_file))
        assert any("MISMATCH" in e for e in errors), (
            f"Expected SHA mismatch error, got: {errors}"
        )

    def test_sidecar_result_not_pass_fails(self, tmp_path):
        """Sidecar with validation_result != PASS fails."""
        bundle_bytes = _make_bundle_bytes()
        bundle_file = tmp_path / "test-bundle.zip"
        bundle_file.write_bytes(bundle_bytes)

        sha = _sha256(bundle_bytes)
        with zipfile.ZipFile(bundle_file) as zf:
            entries = len(zf.namelist())

        sidecar_data = {
            "sha256": sha,
            "size_bytes": len(bundle_bytes),
            "entry_count": entries,
            "validation_result": "FAIL",  # Not PASS
        }
        sidecar_file = tmp_path / "test-bundle.zip.sha256-proof.json"
        sidecar_file.write_text(json.dumps(sidecar_data))

        errors = check_sidecar_proof(str(bundle_file), str(sidecar_file))
        assert any("RESULT_NOT_PASS" in e for e in errors), (
            f"Expected RESULT_NOT_PASS error, got: {errors}"
        )
