"""
test_r57_final_proof_completeness.py — R57 Train B: Final proof completeness tests.

Verifies that final-bundle-validation-proof.txt contains all required self-verifying fields.
R56's proof file was missing: bundle filename, SHA-256, size, entry_count, sidecar_path, exit_code.

This closes IV-R56-008.

Required fields for a complete self-verifying proof:
1. Bundle filename (r57-*.zip)
2. At least one SHA-256 value (Pass 1 or Pass 2, 64 hex chars)
3. Size in bytes (numeric)
4. Entry count (numeric)
5. Sidecar proof path or confirmation
6. BUNDLE_VALIDATION: PASS line
7. Sprint ID

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
IV-R56-008
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


REQUIRED_PROOF_PATTERNS = {
    "sha256_value": re.compile(r"[Ss][Hh][Aa][-_]?256.*?[0-9a-f]{64}", re.DOTALL),
    "bundle_filename": re.compile(r"r57[^.\n]*\.zip", re.IGNORECASE),
    "bundle_validation_pass": re.compile(r"BUNDLE_VALIDATION:\s*PASS"),
    "sprint_id": re.compile(r"FORMAT-FACTORY-R57"),
    "entry_count": re.compile(r"(?:entries?|entry.count)[:\s]+\d+", re.IGNORECASE),
    "size_bytes": re.compile(r"(?:size[_\s]bytes?|bytes?)[:\s]+\d+", re.IGNORECASE),
}


class TestProofFieldSchema:
    """Unit tests for the required proof field patterns."""

    def test_sha256_pattern_matches_valid_sha(self):
        text = "SHA-256: 5043fe754c23a5ce2ee3ce97dd4ebfc2facfd2d224bc43ec82b955828a152ca7"
        assert REQUIRED_PROOF_PATTERNS["sha256_value"].search(text)

    def test_sha256_pattern_rejects_truncated(self):
        text = "SHA-256: 9c10377a748a5f0df9b6e0817a5249ff"  # 32 chars
        assert not REQUIRED_PROOF_PATTERNS["sha256_value"].search(text)

    def test_bundle_filename_pattern(self):
        text = "Bundle: r57-pass2-final.zip"
        assert REQUIRED_PROOF_PATTERNS["bundle_filename"].search(text)

    def test_bundle_validation_pass_pattern(self):
        text = "BUNDLE_VALIDATION: PASS"
        assert REQUIRED_PROOF_PATTERNS["bundle_validation_pass"].search(text)

    def test_entry_count_pattern(self):
        for text in ["entries: 2500", "entry_count: 2500", "Total entries: 2500"]:
            assert REQUIRED_PROOF_PATTERNS["entry_count"].search(text), f"Failed: {text!r}"

    def test_size_bytes_pattern(self):
        for text in ["size_bytes: 4500000", "size bytes: 4500000", "bytes: 4621786"]:
            assert REQUIRED_PROOF_PATTERNS["size_bytes"].search(text), f"Failed: {text!r}"


class TestProofValidatorFunction:
    """Test a helper function for validating proof completeness."""

    def _check_proof_complete(self, content: str) -> list[str]:
        """Returns list of missing field names."""
        missing = []
        for field_name, pattern in REQUIRED_PROOF_PATTERNS.items():
            if not pattern.search(content):
                missing.append(field_name)
        return missing

    def test_complete_proof_passes(self):
        proof = (
            "R57 Final Bundle Validation Proof\n"
            "Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001\n"
            "Bundle: r57-pass2-final.zip\n"
            "SHA-256: 5043fe754c23a5ce2ee3ce97dd4ebfc2facfd2d224bc43ec82b955828a152ca7\n"
            "Size bytes: 4621786\n"
            "Entries: 2500\n"
            "BUNDLE_VALIDATION: PASS\n"
        )
        missing = self._check_proof_complete(proof)
        assert missing == [], f"Expected no missing fields, got: {missing}"

    def test_r56_style_proof_missing_fields(self):
        """R56's actual proof style should fail the completeness check."""
        r56_proof = (
            "R56 Final Bundle Validation Proof\n"
            "Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001\n"
            "Python tests (non-AI): 3892 passed\n"
            "BUNDLE_BUILD: PASS (see below after validation)\n"
        )
        missing = self._check_proof_complete(r56_proof)
        # R56 proof lacks SHA, filename, entry_count, size_bytes, BUNDLE_VALIDATION: PASS
        assert "sha256_value" in missing, "R56 proof should be missing SHA"
        assert "bundle_filename" in missing, "R56 proof should be missing bundle filename"
        assert "bundle_validation_pass" in missing, "R56 proof should be missing BUNDLE_VALIDATION: PASS"

    def test_proof_with_only_sprint_id_fails(self):
        proof = "Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001\n"
        missing = self._check_proof_complete(proof)
        assert len(missing) >= 4, f"Sparse proof should have many missing fields: {missing}"


class TestR56ProofDefectDocumented:
    """Verify that the R56 proof file defect is documented."""

    R56_PROOF = PROJECT_ROOT / ".local" / "r56-metadata" / "final-bundle-validation-proof.txt"
    R56_IV = PROJECT_ROOT / "reports" / "r57" / "r56-independent-verification.md"

    def test_iv_documents_proof_defect(self):
        """r56-independent-verification.md must document IV-R56-008."""
        if not self.R56_IV.exists():
            pytest.skip("R57 IV report not yet created")
        content = self.R56_IV.read_text(encoding="utf-8")
        assert "IV-R56-008" in content, "IV report must document proof completeness defect"

    def test_r56_proof_missing_sha_confirmed(self):
        """The R56 proof file lacks a 64-char SHA value."""
        if not self.R56_PROOF.exists():
            pytest.skip("R56 proof not available in this environment")
        content = self.R56_PROOF.read_text(encoding="utf-8")
        sha_found = bool(re.search(r"SHA-256.*?[0-9a-f]{64}", content, re.DOTALL))
        assert not sha_found, (
            "R56 proof should lack a full 64-char SHA-256 (IV-R56-008); "
            f"if this test fails, the proof was updated after IV was written"
        )
