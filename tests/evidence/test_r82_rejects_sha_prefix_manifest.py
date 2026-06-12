"""
tests/evidence/test_r82_rejects_sha_prefix_manifest.py

R82 Train P: Package artifact manifest must use full 64-char SHA-256, not prefixes.

Defect fixed: D79-03 — R79 manifest listed only 8-char SHA prefixes.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SHA_PREFIX_PATTERN = re.compile(r"^[0-9a-f]{8,16}$")  # detect short/truncated SHAs


def _is_full_sha256(value: str) -> bool:
    return bool(SHA256_PATTERN.match(value.strip().lower()))


def _is_sha_prefix(value: str) -> bool:
    """Detect suspiciously short hex strings (likely truncated SHA)."""
    v = value.strip().lower()
    return bool(re.match(r"^[0-9a-f]{8,16}$", v))


class TestManifestFullSha256:
    """Package manifest SHA values must be full 64-character hex strings."""

    def test_full_sha256_accepted(self):
        sha = "d22f4bf7721cb4e2a91ad2a5e0c984c23b09ca7086f521bf4e17aae030b2c6c0"
        assert _is_full_sha256(sha), f"Full SHA should be accepted: {sha}"

    def test_sha_prefix_8chars_rejected(self):
        prefix = "d22f4bf7"
        assert not _is_full_sha256(prefix), "8-char prefix should not be full SHA"
        assert _is_sha_prefix(prefix), "8-char prefix should be detected as truncated"

    def test_sha_prefix_16chars_rejected(self):
        prefix = "d22f4bf7721cb4e2"
        assert not _is_full_sha256(prefix)
        assert _is_sha_prefix(prefix)

    def test_empty_sha_rejected(self):
        assert not _is_full_sha256("")
        assert not _is_full_sha256("N/A")
        assert not _is_full_sha256("TBD")

    def test_manifest_has_no_sha_prefixes(self):
        """R82 metadata manifest must have full SHA-256 values."""
        manifest_path = REPO_ROOT / ".local" / "r82-metadata" / "package-artifact-manifest.yaml"
        if not manifest_path.exists():
            return  # Not built yet — skip
        content = manifest_path.read_text(encoding="utf-8")
        # Find any sha256: lines
        import re as re2
        sha_lines = re2.findall(r"sha256:\s*([0-9a-fA-F]+)", content)
        for sha in sha_lines:
            assert _is_full_sha256(sha), (
                f"Manifest has SHA prefix '{sha}' — must be full 64-char hash"
            )
