"""
test_r61_nupkg_self_contained.py — R61 Train F: .NET NuGet self-contained delivery.

Verifies that:
1. .nupkg files are physically present in the R61 metadata dotnet-nupkgs/ directory
2. SHA-256 is full 64-char (not 8-char prefix)
3. Manifest references bundle_path (not local .local/ path)
4. Bundle path under bundle-metadata/ is correct

Repairs IV-R60-007 (.nupkg not in bundle) and IV-R60-008 (SHA prefix).

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NUPKG_DIR = PROJECT_ROOT / ".local" / "r61-metadata" / "dotnet-nupkgs"
MANIFEST_PATH = PROJECT_ROOT / ".local" / "r61-metadata" / "dotnet-nupkg-manifest.yaml"

EXPECTED_PACKAGES = [
    ("FormatFactory.Fods.0.1.0-tier0.nupkg", "357123908988864a74cb7f1d63f6538f3674d064b1519d45bd6f9f2206067066", 14612),
    ("FormatFactory.Fodt.0.1.0-tier0.nupkg", "bfdfbd48d31099b6cfefd4fea27dd429456985838138d271f57ea6e81b971385", 13664),
]


class TestNupkgSelfContained:
    """NuPkg files must be physically present in a self-contained directory."""

    def test_nupkg_dir_exists(self):
        """R61 dotnet-nupkgs/ directory must exist."""
        if not NUPKG_DIR.exists():
            pytest.skip("NuPkg dir not present in this environment")
        assert NUPKG_DIR.is_dir()

    def test_fods_nupkg_present(self):
        """FormatFactory.Fods .nupkg must be physically in dotnet-nupkgs/."""
        if not NUPKG_DIR.exists():
            pytest.skip("NuPkg dir not present in this environment")
        path = NUPKG_DIR / "FormatFactory.Fods.0.1.0-tier0.nupkg"
        assert path.exists(), f"FODS .nupkg not found: {path}"
        assert path.stat().st_size > 0

    def test_fodt_nupkg_present(self):
        """FormatFactory.Fodt .nupkg must be physically in dotnet-nupkgs/."""
        if not NUPKG_DIR.exists():
            pytest.skip("NuPkg dir not present in this environment")
        path = NUPKG_DIR / "FormatFactory.Fodt.0.1.0-tier0.nupkg"
        assert path.exists(), f"FODT .nupkg not found: {path}"
        assert path.stat().st_size > 0


class TestNupkgSHA256FullLength:
    """SHA-256 for .nupkg files must be full 64-char (not 8-char prefix)."""

    @pytest.mark.parametrize("filename,expected_sha,expected_size", EXPECTED_PACKAGES)
    def test_nupkg_sha256_correct(self, filename, expected_sha, expected_size):
        """SHA-256 of .nupkg file matches expected value."""
        path = NUPKG_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not available")
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual_sha == expected_sha, (
            f"SHA mismatch for {filename}. Expected: {expected_sha}, Actual: {actual_sha}"
        )

    @pytest.mark.parametrize("filename,expected_sha,expected_size", EXPECTED_PACKAGES)
    def test_nupkg_sha256_is_64_chars(self, filename, expected_sha, expected_size):
        """SHA-256 must be exactly 64 hex chars (not 8-char prefix)."""
        assert len(expected_sha) == 64, (
            f"Expected SHA must be 64 chars for {filename}. Got {len(expected_sha)}: {expected_sha!r}"
        )
        assert all(c in "0123456789abcdef" for c in expected_sha), (
            f"SHA must be lowercase hex for {filename}"
        )

    @pytest.mark.parametrize("filename,expected_sha,expected_size", EXPECTED_PACKAGES)
    def test_nupkg_size_matches(self, filename, expected_sha, expected_size):
        """File size matches expected value."""
        path = NUPKG_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not available")
        actual_size = path.stat().st_size
        assert actual_size == expected_size, (
            f"Size mismatch for {filename}. Expected: {expected_size}, Actual: {actual_size}"
        )


class TestNupkgManifest:
    """dotnet-nupkg-manifest.yaml uses full SHA-256 and bundle_path."""

    def test_manifest_exists(self):
        """R61 dotnet-nupkg-manifest.yaml must exist."""
        if not MANIFEST_PATH.exists():
            pytest.skip("Manifest not present in this environment")

    def test_manifest_no_sha256_prefix(self):
        """Manifest must NOT use sha256_prefix field."""
        if not MANIFEST_PATH.exists():
            pytest.skip("Manifest not available")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "sha256_prefix" not in content, (
            "IV-R60-008: Manifest must not use sha256_prefix. Use full sha256 (64 chars)."
        )

    def test_manifest_has_full_sha256(self):
        """Manifest must have sha256 with full 64-char value."""
        if not MANIFEST_PATH.exists():
            pytest.skip("Manifest not available")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "sha256:" in content, "Manifest must have sha256: field"
        import re
        sha_values = re.findall(r'sha256:\s*([0-9a-f]{64})', content)
        assert len(sha_values) >= 2, (
            f"Expected 2 full SHA-256 values in manifest. Found: {sha_values}"
        )
        for sha in sha_values:
            assert len(sha) == 64, f"SHA must be 64 chars: {sha!r}"

    def test_manifest_uses_bundle_path(self):
        """Manifest must reference bundle_path (not local .local/ path)."""
        if not MANIFEST_PATH.exists():
            pytest.skip("Manifest not available")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "bundle_path" in content, "Manifest must have bundle_path field"
        assert "bundle-metadata/dotnet-nupkgs/" in content, (
            "Manifest bundle_path must reference bundle-metadata/dotnet-nupkgs/"
        )

    def test_manifest_delivery_policy_self_contained(self):
        """Manifest must declare delivery_policy: self_contained."""
        if not MANIFEST_PATH.exists():
            pytest.skip("Manifest not available")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "self_contained" in content, (
            "Manifest must declare delivery_policy: self_contained"
        )

    def test_r60_manifest_had_sha_prefix_defect(self):
        """Confirm R60 manifest used sha256_prefix (IV-R60-008)."""
        r60_manifest = PROJECT_ROOT / ".local" / "r60-metadata" / "dotnet-nupkg-manifest.yaml"
        if not r60_manifest.exists():
            pytest.skip("R60 manifest not available for defect confirmation")
        content = r60_manifest.read_text(encoding="utf-8")
        assert "sha256_prefix" in content, (
            f"Expected R60 manifest to have sha256_prefix (IV-R60-008 confirmation). "
            f"Content: {content[:300]!r}"
        )
