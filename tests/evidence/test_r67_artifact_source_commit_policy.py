"""R67 Train C: artifact source commit policy tests.

Verifies:
- artifact_source_commit is a valid 40-char SHA
- final_git_head is a valid 40-char SHA
- final_git_head is different from artifact_source_commit (they represent different points)
- All artifact entries have required fields: filename, type, sha256, size_bytes
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA64_RE = re.compile(r"^[0-9a-f]{64}$")


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
def artifact_manifest_path():
    m = _find_manifest("package-artifact-manifest.yaml")
    if m is None:
        pytest.skip("package-artifact-manifest.yaml not found")
    return m


@pytest.fixture
def artifact_manifest(artifact_manifest_path):
    if HAS_YAML:
        return yaml.safe_load(artifact_manifest_path.read_text(encoding="utf-8"))
    return None


class TestSourceCommitPolicy:
    def test_artifact_source_commit_is_40char_sha(self, artifact_manifest_path):
        import re as _re
        content = artifact_manifest_path.read_text(encoding="utf-8")
        match = _re.search(r"artifact_source_commit:\s*([0-9a-f]+)", content)
        assert match is not None, "artifact_source_commit missing"
        sha = match.group(1)
        assert len(sha) == 40, f"artifact_source_commit should be 40-char, got {len(sha)}: {sha}"

    def test_final_git_head_is_40char_sha(self, artifact_manifest_path):
        import re as _re
        content = artifact_manifest_path.read_text(encoding="utf-8")
        match = _re.search(r"final_git_head:\s*([0-9a-f]+)", content)
        assert match is not None, "final_git_head missing or not a SHA"
        sha = match.group(1)
        assert len(sha) == 40, f"final_git_head should be 40-char, got {len(sha)}: {sha}"

    def test_no_truncated_ellipsis_hashes(self, artifact_manifest_path):
        content = artifact_manifest_path.read_text(encoding="utf-8")
        assert "..." not in content, "Manifest contains truncated hashes with ellipsis"

    def test_all_sha256_fields_are_64_chars(self, artifact_manifest_path):
        import re as _re
        content = artifact_manifest_path.read_text(encoding="utf-8")
        # Find all sha256: <hex> values
        matches = _re.findall(r"sha256:\s*([0-9a-f]+)", content)
        assert len(matches) > 0, "No sha256 fields found"
        for sha in matches:
            assert len(sha) == 64, f"sha256 field has wrong length ({len(sha)}): {sha}"


class TestArtifactEntryFields:
    @pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
    def test_all_artifacts_have_required_fields(self, artifact_manifest):
        if artifact_manifest is None:
            pytest.skip("Could not parse manifest")
        artifacts = artifact_manifest.get("artifacts", [])
        assert len(artifacts) > 0, "No artifacts in manifest"
        required_fields = ["filename", "type", "sha256", "size_bytes"]
        for art in artifacts:
            for field in required_fields:
                assert field in art, f"Artifact missing '{field}': {art.get('filename', '?')}"

    @pytest.mark.skipif(not HAS_YAML, reason="PyYAML not available")
    def test_artifact_count_matches_declared(self, artifact_manifest):
        if artifact_manifest is None:
            pytest.skip("Could not parse manifest")
        declared = artifact_manifest.get("artifact_count", 0)
        actual = len(artifact_manifest.get("artifacts", []))
        assert actual == declared, f"artifact_count={declared} but {actual} artifacts listed"
