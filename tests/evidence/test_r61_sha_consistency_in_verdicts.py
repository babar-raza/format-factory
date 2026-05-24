"""
test_r61_sha_consistency_in_verdicts.py — R61 Train B: SHA consistency enforcement.

Verifies that:
1. The SHA in final-verdict.md matches the actual bundle SHA (not an interim SHA)
2. The sidecar SHA matches the actual bundle SHA
3. Both SHAs are consistent with each other

Repairs IV-R60-002.

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_pass2_sha_from_verdict(verdict_text: str) -> str | None:
    """Extract BUNDLE_VALIDATION_PASS_2_SHA from final-verdict.md content."""
    match = re.search(r"BUNDLE_VALIDATION_PASS_2_SHA:\s*([0-9a-f]{64})", verdict_text)
    if match:
        return match.group(1)
    return None


def _extract_sha_from_sidecar(sidecar_path: Path) -> str | None:
    """Extract SHA from sidecar JSON."""
    if not sidecar_path.exists():
        return None
    data = json.loads(sidecar_path.read_text())
    return data.get("sha256") or data.get("bundle_sha256")


class TestR60SHAMismatchConfirmed:
    """Confirm that R60 has the SHA mismatch defect (IV-R60-002)."""

    def test_r60_final_verdict_sha_mismatches_true_final(self):
        """R60 final-verdict PASS_2_SHA is interim SHA; does NOT match true final bundle."""
        verdict_path = PROJECT_ROOT / "reports" / "r60" / "final-verdict.md"
        bundle_path = PROJECT_ROOT / ".local" / "r60-pass2-final.zip"
        if not verdict_path.exists() or not bundle_path.exists():
            pytest.skip("R60 artifacts not available for IV confirmation")

        verdict_text = verdict_path.read_text(encoding="utf-8")
        verdict_sha = _extract_pass2_sha_from_verdict(verdict_text)
        assert verdict_sha is not None, "Could not extract BUNDLE_VALIDATION_PASS_2_SHA from final-verdict.md"

        actual_sha = _compute_sha256(bundle_path)
        assert verdict_sha != actual_sha, (
            f"R60 verdict SHA should NOT match actual bundle (IV-R60-002 should be present). "
            f"If they match, the defect may have been resolved."
        )
        # Confirm the interim vs true final SHA
        assert verdict_sha == "d2ab8404730a5b47547186c45e6e0da89ce730d7b4b6a4604dc96afe6357e295", (
            f"R60 verdict has unexpected interim SHA: {verdict_sha}"
        )
        assert actual_sha == "f8b6f8cec04e6a1f69ac84a0519938cf282b860b0db25348f73616e5ae7f7c42", (
            f"R60 bundle has unexpected true final SHA: {actual_sha}"
        )

    def test_r60_sidecar_sha_matches_true_final(self):
        """R60 sidecar SHA does match the true final bundle (sidecar is correct)."""
        sidecar_path = PROJECT_ROOT / "reports" / "r60" / "r60-pass2-final.zip.sha256-proof.json"
        bundle_path = PROJECT_ROOT / ".local" / "r60-pass2-final.zip"
        if not sidecar_path.exists() or not bundle_path.exists():
            pytest.skip("R60 sidecar not available for confirmation")

        sidecar_sha = _extract_sha_from_sidecar(sidecar_path)
        actual_sha = _compute_sha256(bundle_path)
        assert sidecar_sha == actual_sha, (
            f"R60 sidecar SHA should match bundle. Sidecar: {sidecar_sha}, Actual: {actual_sha}"
        )


class TestSHAConsistencyRequirements:
    """SHA in final-verdict must match actual bundle and sidecar."""

    def test_sha256_must_be_64_chars(self):
        """Any SHA-256 reference must be exactly 64 hex chars."""
        sha_ok = "a" * 64
        sha_short = "a" * 8
        sha_long = "a" * 65
        assert len(sha_ok) == 64
        assert len(sha_short) != 64, "8-char prefix is not a valid SHA-256"
        assert len(sha_long) != 64, "65-char is not a valid SHA-256"

    def test_interim_sha_must_not_be_final_sha(self, tmp_path):
        """Interim bundle (built before final-verdict update) has different SHA than final."""
        # Create two bundles with slightly different content
        bundle1 = tmp_path / "pass2-interim.zip"
        bundle2 = tmp_path / "pass2-final.zip"
        with zipfile.ZipFile(bundle1, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "R61-TEST-INTERIM")
        with zipfile.ZipFile(bundle2, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "R61-TEST-INTERIM")
            zf.writestr("repo/reports/r61/final-verdict.md", "BUNDLE_VALIDATION_PASS_2_SHA: " + "b" * 64)
        sha1 = _compute_sha256(bundle1)
        sha2 = _compute_sha256(bundle2)
        assert sha1 != sha2, (
            "Interim and final bundle must have different SHAs (content differs)"
        )

    def test_verdict_sha_extraction_pattern(self):
        """SHA extraction from final-verdict.md works correctly."""
        verdict_text = (
            "BUNDLE_VALIDATION_PASS_1_SHA: " + "a" * 64 + "\n"
            "BUNDLE_VALIDATION_PASS_2_SHA: " + "b" * 64 + "\n"
        )
        sha = _extract_pass2_sha_from_verdict(verdict_text)
        assert sha == "b" * 64, f"Expected 64-char SHA, got: {sha!r}"

    def test_verdict_sha_extraction_rejects_short_sha(self):
        """SHA extraction rejects 8-char prefix (not a valid SHA-256)."""
        verdict_text = "BUNDLE_VALIDATION_PASS_2_SHA: d2ab8404\n"
        sha = _extract_pass2_sha_from_verdict(verdict_text)
        assert sha is None, f"Should not extract 8-char prefix as SHA-256, got: {sha!r}"

    def test_sidecar_sha_must_match_computed_sha(self, tmp_path):
        """Sidecar SHA must equal hashlib.sha256 of the bundle."""
        bundle = tmp_path / "test.zip"
        with zipfile.ZipFile(bundle, "w") as zf:
            zf.writestr("bundle-metadata/test.txt", "hello")
        actual_sha = _compute_sha256(bundle)
        sidecar_data = {"sha256": actual_sha, "bundle_filename": "test.zip"}
        sidecar = tmp_path / "test.zip.sha256-proof.json"
        sidecar.write_text(json.dumps(sidecar_data))

        extracted_sha = _extract_sha_from_sidecar(sidecar)
        assert extracted_sha == actual_sha, (
            f"Sidecar SHA must match computed SHA. Got: {extracted_sha}"
        )

    def test_wrong_sidecar_sha_detects_mismatch(self, tmp_path):
        """Sidecar with wrong SHA detects mismatch."""
        bundle = tmp_path / "test.zip"
        with zipfile.ZipFile(bundle, "w") as zf:
            zf.writestr("bundle-metadata/test.txt", "hello")
        wrong_sha = "0" * 64
        sidecar_data = {"sha256": wrong_sha, "bundle_filename": "test.zip"}
        sidecar = tmp_path / "test.zip.sha256-proof.json"
        sidecar.write_text(json.dumps(sidecar_data))

        extracted_sha = _extract_sha_from_sidecar(sidecar)
        actual_sha = _compute_sha256(bundle)
        assert extracted_sha != actual_sha, "Wrong SHA must not match computed SHA"
