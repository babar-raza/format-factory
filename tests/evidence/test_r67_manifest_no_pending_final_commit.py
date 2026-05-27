"""R67 Train C: package-artifact-manifest and dotnet-nupkg-manifest must not contain PENDING_FINAL_COMMIT.

Covers IV-R67-002: both manifests had final_git_head: PENDING_FINAL_COMMIT in R66.
R67 Train C requires both manifests to have actual full-SHA final_git_head fields.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FORBIDDEN = "PENDING_FINAL_COMMIT"


def _find_manifest(name: str) -> Path | None:
    """Find manifest in r67-metadata or r66-metadata."""
    for run in ["r67", "r66"]:
        p = PROJECT_ROOT / ".local" / f"{run}-metadata" / name
        if p.is_file():
            return p
    # Also check bundle-metadata (extracted bundle)
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


class TestArtifactManifestNoPending:
    def test_no_pending_final_commit(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        assert _FORBIDDEN not in content, (
            f"{artifact_manifest.name} contains '{_FORBIDDEN}' — must be filled with actual SHA"
        )

    def test_final_git_head_present(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        assert "final_git_head:" in content, "final_git_head field missing from manifest"

    def test_final_git_head_looks_like_sha(self, artifact_manifest):
        import re
        content = artifact_manifest.read_text(encoding="utf-8")
        match = re.search(r"final_git_head:\s*([0-9a-f]+)", content)
        assert match is not None, "final_git_head is missing or not a hex SHA"
        sha = match.group(1)
        assert len(sha) == 40, f"final_git_head should be 40-char SHA, got {len(sha)}: {sha}"

    def test_artifact_source_commit_present(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        assert "artifact_source_commit:" in content

    def test_no_pending_in_any_field(self, artifact_manifest):
        content = artifact_manifest.read_text(encoding="utf-8")
        for token in ("PENDING_FINAL_COMMIT", "PENDING", "to be completed", "to be filled"):
            assert token not in content, f"Forbidden token '{token}' found in {artifact_manifest.name}"


class TestDotnetManifestNoPending:
    def test_no_pending_final_commit(self, dotnet_manifest):
        content = dotnet_manifest.read_text(encoding="utf-8")
        assert _FORBIDDEN not in content, (
            f"{dotnet_manifest.name} contains '{_FORBIDDEN}'"
        )

    def test_final_git_head_present(self, dotnet_manifest):
        content = dotnet_manifest.read_text(encoding="utf-8")
        assert "final_git_head:" in content

    def test_final_git_head_looks_like_sha(self, dotnet_manifest):
        import re
        content = dotnet_manifest.read_text(encoding="utf-8")
        match = re.search(r"final_git_head:\s*([0-9a-f]+)", content)
        assert match is not None, "final_git_head is missing or not a hex SHA"
        sha = match.group(1)
        assert len(sha) == 40, f"final_git_head should be 40-char SHA, got {len(sha)}: {sha}"
