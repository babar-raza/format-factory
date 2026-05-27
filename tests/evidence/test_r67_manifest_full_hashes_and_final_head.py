"""R67 Train C: manifest full hashes and final_git_head completeness.

All 22 artifacts must have full 64-char sha256.
Both manifests must have final_git_head (non-placeholder, 40-char SHA).
Dotnet nupkg manifest must have filename, size_bytes, sha256.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _find_manifest(name: str) -> Path | None:
    for run in ["r67", "r66"]:
        p = PROJECT_ROOT / ".local" / f"{run}-metadata" / name
        if p.is_file():
            return p
    p = PROJECT_ROOT / "bundle-metadata" / name
    if p.is_file():
        return p
    return None


@pytest.fixture
def artifact_manifest():
    m = _find_manifest("package-artifact-manifest.yaml")
    if m is None:
        pytest.skip("package-artifact-manifest.yaml not found")
    return m


@pytest.fixture
def dotnet_manifest():
    m = _find_manifest("dotnet-nupkg-manifest.yaml")
    if m is None:
        pytest.skip("dotnet-nupkg-manifest.yaml not found")
    return m


class TestArtifactManifestHashes:
    def test_all_sha256_are_64_chars(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        hashes = re.findall(r"sha256:\s*([0-9a-f]+)", content)
        assert len(hashes) > 0
        short = [h for h in hashes if len(h) != 64]
        assert not short, f"Truncated hashes found: {short}"

    def test_no_ellipsis_truncation(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        lines_with_hash = [l for l in content.splitlines() if "sha256:" in l]
        for line in lines_with_hash:
            assert "..." not in line, f"Truncated hash in line: {line.strip()}"

    def test_final_git_head_40_chars(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        match = re.search(r"final_git_head:\s*([0-9a-f]{40})", content)
        assert match is not None, "final_git_head must be a 40-char SHA in artifact manifest"

    def test_no_pending_final_commit(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        assert "PENDING_FINAL_COMMIT" not in content

    def test_artifact_count_at_least_22(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        hashes = re.findall(r"sha256:\s*([0-9a-f]{64})", content)
        assert len(hashes) >= 22, f"Expected at least 22 artifacts with full hashes, got {len(hashes)}"


class TestDotnetManifestHashes:
    def test_all_sha256_are_64_chars(self, dotnet_manifest):
        content = dotnet_manifest.read_text(encoding="utf-8")
        hashes = re.findall(r"sha256:\s*([0-9a-f]+)", content)
        assert len(hashes) >= 2, "Expected at least 2 dotnet nupkg SHA-256 hashes"
        short = [h for h in hashes if len(h) != 64]
        assert not short, f"Truncated dotnet hashes: {short}"

    def test_filenames_present(self, dotnet_manifest):
        content = dotnet_manifest.read_text(encoding="utf-8")
        assert "filename:" in content, "dotnet manifest missing filename fields"

    def test_size_bytes_present(self, dotnet_manifest):
        content = dotnet_manifest.read_text(encoding="utf-8")
        assert "size_bytes:" in content

    def test_final_git_head_40_chars(self, dotnet_manifest):
        content = dotnet_manifest.read_text(encoding="utf-8")
        match = re.search(r"final_git_head:\s*([0-9a-f]{40})", content)
        assert match is not None, "final_git_head must be a 40-char SHA in dotnet manifest"

    def test_no_pending_final_commit(self, dotnet_manifest):
        content = dotnet_manifest.read_text(encoding="utf-8")
        assert "PENDING_FINAL_COMMIT" not in content
