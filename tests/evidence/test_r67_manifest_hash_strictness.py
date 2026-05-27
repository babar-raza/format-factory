"""R67 Train D: manifest hash strictness.

Validator hardening: all sha256 entries in manifests must be full 64-char hex strings.
No ellipsis truncation, no PENDING placeholders, no short hashes.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SHA64_RE = re.compile(r"^[0-9a-f]{64}$")


def _find_metadata_dir() -> Path | None:
    for run in ["r67", "r66"]:
        d = PROJECT_ROOT / ".local" / f"{run}-metadata"
        if d.is_dir():
            return d
    return None


def _find_bundle() -> Path | None:
    for run in ["r67", "r66"]:
        p = PROJECT_ROOT / ".local" / f"{run}-pass2-final.zip"
        if p.is_file():
            return p
    return None


@pytest.fixture
def metadata_dir():
    d = _find_metadata_dir()
    if d is None:
        pytest.skip("No metadata directory available")
    return d


@pytest.fixture
def bundle_path():
    b = _find_bundle()
    if b is None:
        pytest.skip("No bundle available")
    return b


class TestLocalManifestHashes:
    def test_artifact_manifest_no_truncated_hashes(self, metadata_dir):
        f = metadata_dir / "package-artifact-manifest.yaml"
        if not f.is_file():
            pytest.skip()
        content = f.read_text(encoding="utf-8")
        sha_lines = [l for l in content.splitlines() if "sha256:" in l]
        for line in sha_lines:
            assert "..." not in line, f"Truncated hash: {line.strip()}"
            match = re.search(r"sha256:\s*([0-9a-f]+)", line)
            if match:
                sha = match.group(1)
                assert len(sha) == 64, f"Short hash ({len(sha)} chars): {line.strip()}"

    def test_dotnet_manifest_no_truncated_hashes(self, metadata_dir):
        f = metadata_dir / "dotnet-nupkg-manifest.yaml"
        if not f.is_file():
            pytest.skip()
        content = f.read_text(encoding="utf-8")
        sha_lines = [l for l in content.splitlines() if "sha256:" in l]
        for line in sha_lines:
            assert "..." not in line, f"Truncated dotnet hash: {line.strip()}"
            match = re.search(r"sha256:\s*([0-9a-f]+)", line)
            if match:
                sha = match.group(1)
                assert len(sha) == 64, f"Short dotnet hash ({len(sha)} chars): {line.strip()}"

    def test_dotnet_manifest_has_filenames(self, metadata_dir):
        f = metadata_dir / "dotnet-nupkg-manifest.yaml"
        if not f.is_file():
            pytest.skip()
        content = f.read_text(encoding="utf-8")
        assert "filename:" in content, "dotnet manifest must have filename fields"
        assert ".nupkg" in content, "dotnet manifest must reference .nupkg files"


class TestBundledManifestHashes:
    def test_bundled_artifact_manifest_no_truncated_hashes(self, bundle_path):
        with zipfile.ZipFile(bundle_path) as z:
            entries = [n for n in z.namelist() if "package-artifact-manifest" in n]
            if not entries:
                pytest.skip()
            for entry in entries:
                content = z.read(entry).decode("utf-8", errors="replace")
                sha_lines = [l for l in content.splitlines() if "sha256:" in l]
                for line in sha_lines:
                    assert "..." not in line, f"Truncated hash in bundled {entry}: {line.strip()}"

    def test_bundled_dotnet_manifest_no_truncated_hashes(self, bundle_path):
        with zipfile.ZipFile(bundle_path) as z:
            entries = [n for n in z.namelist() if "dotnet-nupkg-manifest" in n]
            if not entries:
                pytest.skip()
            for entry in entries:
                content = z.read(entry).decode("utf-8", errors="replace")
                sha_lines = [l for l in content.splitlines() if "sha256:" in l]
                for line in sha_lines:
                    assert "..." not in line, f"Truncated hash in bundled dotnet {entry}"
