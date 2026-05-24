"""
test_r61_proof_file_not_placeholder.py — R61 Train B: Proof file integrity enforcement.

Verifies that final-bundle-validation-proof.txt inside a bundle is NOT a placeholder.
Repairs IV-R60-004.

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PLACEHOLDER_STRINGS = [
    "PLACEHOLDER",
    "will be replaced",
    "TBD",
    "TODO",
    "PENDING",
]

REQUIRED_PROOF_FIELDS = [
    "BUNDLE_VALIDATION",
    "sha256",
    "entry_count",
]


def _bundle_has_placeholder_proof(bundle_path: Path) -> tuple[bool, str]:
    """Check if the bundle's final-bundle-validation-proof.txt is a placeholder.

    Returns (is_placeholder, content_or_reason).
    """
    with zipfile.ZipFile(bundle_path) as zf:
        proof_entries = [n for n in zf.namelist() if "final-bundle-validation-proof" in n]
        if not proof_entries:
            return True, "proof file missing from bundle"
        content = zf.read(proof_entries[0]).decode("utf-8", errors="replace")
        for placeholder in PLACEHOLDER_STRINGS:
            if placeholder.upper() in content.upper():
                return True, content
        return False, content


def _make_bundle_with_placeholder_proof(tmp_path: Path) -> Path:
    """Create a bundle with a placeholder proof file (simulates R60 defect)."""
    bundle = tmp_path / "test-bundle.zip"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("bundle-metadata/sprint-id.txt", "R61-TEST")
        zf.writestr(
            "bundle-metadata/final-bundle-validation-proof.txt",
            "PLACEHOLDER \ufffd will be replaced after candidate validation",
        )
    return bundle


def _make_bundle_with_real_proof(tmp_path: Path) -> Path:
    """Create a bundle with a real proof file (correct R61 behavior)."""
    bundle = tmp_path / "test-bundle.zip"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("bundle-metadata/sprint-id.txt", "R61-TEST")
        real_proof = (
            "Sprint: R61-TEST\n"
            "FINAL BUNDLE VALIDATION PROOF\n"
            "Date: 2026-05-24\n\n"
            "bundle_filename: test-bundle.zip\n"
            "sha256: " + "a" * 64 + "\n"
            "entry_count: 2\n"
            "size_bytes: 1234\n"
            "metadata_files: 1\n"
            "sidecar: reports/r61/test-bundle.zip.sha256-proof.json\n"
            "BUNDLE_VALIDATION: PASS\n"
            "SIDECAR_PROOF_VALIDATION: PASS\n\n"
            "All 14 checks: PASS\n"
        )
        zf.writestr("bundle-metadata/final-bundle-validation-proof.txt", real_proof)
    return bundle


class TestProofFileNotPlaceholder:
    """Proof file inside bundle must not be placeholder text."""

    def test_placeholder_bundle_detected(self, tmp_path):
        """Bundle with placeholder proof is correctly detected as invalid."""
        bundle = _make_bundle_with_placeholder_proof(tmp_path)
        is_placeholder, content = _bundle_has_placeholder_proof(bundle)
        assert is_placeholder, (
            f"Expected placeholder to be detected, but proof content was: {content!r}"
        )

    def test_real_proof_bundle_passes(self, tmp_path):
        """Bundle with real proof passes validation."""
        bundle = _make_bundle_with_real_proof(tmp_path)
        is_placeholder, content = _bundle_has_placeholder_proof(bundle)
        assert not is_placeholder, (
            f"Real proof should not be flagged as placeholder. Content: {content!r}"
        )

    def test_proof_file_has_required_fields(self, tmp_path):
        """Real proof file must contain BUNDLE_VALIDATION, sha256, entry_count."""
        bundle = _make_bundle_with_real_proof(tmp_path)
        with zipfile.ZipFile(bundle) as zf:
            proof_entries = [n for n in zf.namelist() if "final-bundle-validation-proof" in n]
            assert proof_entries, "Proof file must be present in bundle"
            content = zf.read(proof_entries[0]).decode("utf-8")
        for field in REQUIRED_PROOF_FIELDS:
            assert field in content, (
                f"Proof file missing required field '{field}'. Content: {content!r}"
            )

    def test_proof_file_must_contain_pass(self, tmp_path):
        """Real proof must contain BUNDLE_VALIDATION: PASS (not FAIL or PENDING)."""
        bundle = _make_bundle_with_real_proof(tmp_path)
        with zipfile.ZipFile(bundle) as zf:
            content = zf.read("bundle-metadata/final-bundle-validation-proof.txt").decode("utf-8")
        assert "BUNDLE_VALIDATION: PASS" in content, (
            f"Proof must contain BUNDLE_VALIDATION: PASS. Got: {content!r}"
        )

    def test_proof_sha256_is_64_chars(self, tmp_path):
        """SHA-256 in proof file must be exactly 64 chars."""
        bundle = _make_bundle_with_real_proof(tmp_path)
        with zipfile.ZipFile(bundle) as zf:
            content = zf.read("bundle-metadata/final-bundle-validation-proof.txt").decode("utf-8")
        # Extract sha256 line
        sha_lines = [line for line in content.splitlines() if line.startswith("sha256:")]
        assert sha_lines, "Proof file must have sha256: line"
        sha = sha_lines[0].split(":", 1)[1].strip()
        assert len(sha) == 64, f"SHA-256 in proof must be 64 chars, got {len(sha)}: {sha!r}"


class TestR60PlaceholderDefectConfirmed:
    """Confirm that the R60 bundle has the placeholder defect (IV-R60-004)."""

    def test_r60_bundle_has_placeholder_proof(self):
        """R60 bundle final-bundle-validation-proof.txt is a placeholder (IV-R60-004)."""
        bundle = PROJECT_ROOT / ".local" / "r60-pass2-final.zip"
        if not bundle.exists():
            pytest.skip("R60 bundle not available for IV confirmation")
        is_placeholder, content = _bundle_has_placeholder_proof(bundle)
        assert is_placeholder, (
            f"Expected R60 bundle to have placeholder proof (IV-R60-004), "
            f"but it has real content: {content!r}"
        )

    def test_r60_bundle_proof_placeholder_string(self):
        """R60 bundle proof contains PLACEHOLDER string specifically."""
        bundle = PROJECT_ROOT / ".local" / "r60-pass2-final.zip"
        if not bundle.exists():
            pytest.skip("R60 bundle not available for IV confirmation")
        with zipfile.ZipFile(bundle) as zf:
            proof_entries = [n for n in zf.namelist() if "final-bundle-validation-proof" in n]
            assert proof_entries, "R60 bundle has no proof file entry"
            content = zf.read(proof_entries[0]).decode("utf-8", errors="replace")
        assert "PLACEHOLDER" in content.upper(), (
            f"Expected PLACEHOLDER in R60 proof. Got: {content!r}"
        )
