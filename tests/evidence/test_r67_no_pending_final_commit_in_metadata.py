"""R67 Train D: no PENDING_FINAL_COMMIT in any bundled metadata file.

Validator hardening: the bundle validator must detect PENDING_FINAL_COMMIT
as a forbidden token in metadata files.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = "PENDING_FINAL_COMMIT"


def _find_bundle() -> Path | None:
    for run in ["r67", "r66"]:
        p = PROJECT_ROOT / ".local" / f"{run}-pass2-final.zip"
        if p.is_file():
            return p
    return None


def _find_metadata_dir() -> Path | None:
    for run in ["r67", "r66"]:
        d = PROJECT_ROOT / ".local" / f"{run}-metadata"
        if d.is_dir():
            return d
    return None


@pytest.fixture
def bundle_path():
    b = _find_bundle()
    if b is None:
        pytest.skip("No evidence bundle available")
    return b


@pytest.fixture
def metadata_dir():
    d = _find_metadata_dir()
    if d is None:
        pytest.skip("No metadata directory available")
    return d


class TestNoPendingFinalCommitInMetadata:
    def test_package_artifact_manifest_no_pending(self, metadata_dir):
        f = metadata_dir / "package-artifact-manifest.yaml"
        if not f.is_file():
            pytest.skip("package-artifact-manifest.yaml not found")
        assert FORBIDDEN not in f.read_text(encoding="utf-8")

    def test_dotnet_nupkg_manifest_no_pending(self, metadata_dir):
        f = metadata_dir / "dotnet-nupkg-manifest.yaml"
        if not f.is_file():
            pytest.skip("dotnet-nupkg-manifest.yaml not found")
        assert FORBIDDEN not in f.read_text(encoding="utf-8")

    def test_final_bundle_validation_proof_no_pending(self, metadata_dir):
        f = metadata_dir / "final-bundle-validation-proof.txt"
        if not f.is_file():
            pytest.skip("final-bundle-validation-proof.txt not found")
        assert FORBIDDEN not in f.read_text(encoding="utf-8", errors="replace")

    def test_external_sidecar_proof_no_pending(self, metadata_dir):
        f = metadata_dir / "external-sidecar-proof-summary.txt"
        if not f.is_file():
            pytest.skip("external-sidecar-proof-summary.txt not found")
        assert FORBIDDEN not in f.read_text(encoding="utf-8", errors="replace")


class TestBundledMetadataNoForbiddenTokens:
    """In the bundled evidence ZIP, no metadata file should contain PENDING_FINAL_COMMIT."""

    FORBIDDEN_TOKENS = [
        "PENDING_FINAL_COMMIT",
        "to be completed",
        "to be generated",
        "to be confirmed",
    ]

    def test_bundled_package_artifact_manifest_clean(self, bundle_path):
        with zipfile.ZipFile(bundle_path) as z:
            names = z.namelist()
            manifest_entries = [n for n in names if "package-artifact-manifest" in n]
            if not manifest_entries:
                pytest.skip("No package-artifact-manifest in bundle")
            for entry in manifest_entries:
                content = z.read(entry).decode("utf-8", errors="replace")
                for token in self.FORBIDDEN_TOKENS:
                    assert token not in content, f"'{token}' found in bundled {entry}"

    def test_bundled_dotnet_manifest_clean(self, bundle_path):
        with zipfile.ZipFile(bundle_path) as z:
            names = z.namelist()
            manifest_entries = [n for n in names if "dotnet-nupkg-manifest" in n]
            if not manifest_entries:
                pytest.skip("No dotnet-nupkg-manifest in bundle")
            for entry in manifest_entries:
                content = z.read(entry).decode("utf-8", errors="replace")
                for token in self.FORBIDDEN_TOKENS:
                    assert token not in content, f"'{token}' found in bundled {entry}"
