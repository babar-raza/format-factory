"""R66 Train E: artifact manifest must have full 64-char SHA-256 values."""

import re
import sys
from pathlib import Path

_tools = Path(__file__).resolve().parents[2]
if str(_tools) not in sys.path:
    sys.path.insert(0, str(_tools))

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_CANDIDATES = [
    PROJECT_ROOT / ".local" / "r66-metadata" / "package-artifact-manifest.yaml",
    PROJECT_ROOT / ".local" / "r65-metadata" / "package-artifact-manifest.yaml",
]


def _find_manifest():
    for p in MANIFEST_CANDIDATES:
        if p.exists():
            return p
    return None


def _parse_manifest_artifacts(text):
    """Extract sha256 values from manifest."""
    sha_pattern = re.compile(r"sha256:\s*([a-fA-F0-9.]+)")
    return sha_pattern.findall(text)


class TestArtifactManifestFullHashes:
    def _get_manifest(self):
        p = _find_manifest()
        if p is None:
            pytest.skip("No artifact manifest found")
        return p.read_text(encoding="utf-8")

    def test_no_truncated_hashes(self):
        content = self._get_manifest()
        hashes = _parse_manifest_artifacts(content)
        assert len(hashes) > 0, "No sha256 values found in manifest"
        for h in hashes:
            assert "..." not in h, f"Truncated hash found: {h}"

    def test_all_hashes_64_chars(self):
        content = self._get_manifest()
        hashes = _parse_manifest_artifacts(content)
        for h in hashes:
            assert len(h) == 64, f"Hash not 64 chars: {h} (len={len(h)})"
            assert re.match(r"^[a-f0-9]{64}$", h), f"Hash not valid hex: {h}"

    def test_artifact_count_matches_entries(self):
        content = self._get_manifest()
        count_match = re.search(r"artifact_count:\s*(\d+)", content)
        if count_match:
            claimed = int(count_match.group(1))
            hashes = _parse_manifest_artifacts(content)
            assert len(hashes) == claimed, f"Claimed {claimed} artifacts but found {len(hashes)} hashes"

    def test_each_artifact_has_filename(self):
        content = self._get_manifest()
        filenames = re.findall(r"filename:\s*(\S+)", content)
        hashes = _parse_manifest_artifacts(content)
        assert len(filenames) == len(hashes), f"filename count ({len(filenames)}) != hash count ({len(hashes)})"

    def test_each_artifact_has_size(self):
        content = self._get_manifest()
        sizes = re.findall(r"size_bytes:\s*(\d+)", content)
        hashes = _parse_manifest_artifacts(content)
        assert len(sizes) == len(hashes), f"size_bytes count ({len(sizes)}) != hash count ({len(hashes)})"


class TestDotnetNupkgManifestFullHashes:
    def _get_manifest(self):
        candidates = [
            PROJECT_ROOT / ".local" / "r66-metadata" / "dotnet-nupkg-manifest.yaml",
            PROJECT_ROOT / ".local" / "r65-metadata" / "dotnet-nupkg-manifest.yaml",
        ]
        for p in candidates:
            if p.exists():
                return p.read_text(encoding="utf-8")
        pytest.skip("No dotnet nupkg manifest found")

    def test_nupkg_has_full_sha256(self):
        content = self._get_manifest()
        hashes = re.findall(r"sha256:\s*([a-fA-F0-9.]+)", content)
        assert len(hashes) >= 2, f"Expected at least 2 nupkg hashes, found {len(hashes)}"
        for h in hashes:
            assert len(h) == 64, f"Nupkg hash not 64 chars: {h}"
            assert "..." not in h

    def test_nupkg_has_filename(self):
        content = self._get_manifest()
        filenames = re.findall(r"filename:\s*(\S+\.nupkg)", content)
        assert len(filenames) >= 2

    def test_nupkg_has_size(self):
        content = self._get_manifest()
        sizes = re.findall(r"size_bytes:\s*(\d+)", content)
        assert len(sizes) >= 2
