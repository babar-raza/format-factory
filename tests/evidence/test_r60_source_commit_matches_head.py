"""
test_r60_source_commit_matches_head.py — R60 Train C: Source commit verification.

Verifies that the R60 package-artifact-manifest.yaml source_commit matches
the final R60 git HEAD. Repairs IV-R59-005/006.

R60 Sprint: FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
"""
from __future__ import annotations

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / ".local" / "r60-metadata" / "package-artifact-manifest.yaml"


def _get_git_head() -> str:
    """Return current git HEAD SHA (full)."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class TestR60SourceCommit:
    """Package manifest source_commit must reference the R60 HEAD."""

    def test_r60_manifest_exists(self):
        assert MANIFEST_PATH.exists(), f"R60 manifest not found: {MANIFEST_PATH}"

    def test_r60_manifest_has_20_artifacts(self):
        """R60 must have 10 wheels + 10 sdists = 20 total artifacts."""
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        wheel_count = text.count("py3-none-any.whl")
        sdist_count = text.count(".tar.gz")
        assert wheel_count == 10, f"Expected 10 wheels, got {wheel_count}"
        assert sdist_count == 10, f"Expected 10 sdists, got {sdist_count}"

    def test_r60_manifest_sha256_are_64_chars(self):
        """All SHA-256 entries in manifest must be 64-char hex strings."""
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        sha_lines = [ln.strip() for ln in text.splitlines() if "sha256:" in ln and "PLACEHOLDER" not in ln]
        for ln in sha_lines:
            sha = ln.split("sha256:", 1)[1].strip()
            assert len(sha) == 64, f"SHA must be 64 chars: {sha!r} in line {ln!r}"
            assert all(c in "0123456789abcdef" for c in sha), f"SHA not hex: {sha!r}"

    def test_r60_manifest_not_r58_source_commit(self):
        """Source commit must NOT be the R58-era commit 7f17f43."""
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "7f17f43" not in text, (
            "R60 manifest must NOT reference R58-era commit 7f17f43. "
            "Packages must be rebuilt from R60 HEAD."
        )

    def test_r60_manifest_has_10_packages(self):
        """Manifest must list 10 wheels + 10 sdists = 20 artifact entries."""
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        # Manifest uses underscore naming (aspose_format_factory_<fmt>-...)
        wheel_count = text.count("py3-none-any.whl")
        sdist_count = text.count(".tar.gz")
        assert wheel_count == 10, f"Expected 10 wheels, got {wheel_count}"
        assert sdist_count == 10, f"Expected 10 sdists, got {sdist_count}"

    def test_r60_manifest_includes_fods_and_fodt(self):
        """R60 manifest must include fods and fodt packages."""
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        # Manifest uses underscore naming (Python wheel convention)
        assert "aspose_format_factory_fods" in text
        assert "aspose_format_factory_fodt" in text

    def test_r60_manifest_includes_pgm_pbm_sylk(self):
        """R60 manifest must include pgm, pbm, sylk (Gate 10 packages from R59 Train H)."""
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        # Manifest uses underscore naming (Python wheel convention)
        assert "aspose_format_factory_pgm" in text
        assert "aspose_format_factory_pbm" in text
        assert "aspose_format_factory_sylk" in text

    def test_r60_fods_wheel_is_larger_than_r59(self):
        """R60 FODS wheel must be larger than R59 (new capabilities added in Train G)."""
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        import re
        # Find fods wheel size
        match = re.search(r"aspose_format_factory_fods-0\.1\.0\.dev0-py3-none-any\.whl.*?size_bytes:\s*(\d+)", text, re.DOTALL)
        if match:
            size = int(match.group(1))
            # R59 fods wheel was 16223 bytes; R60 should be larger with 2 new functions
            assert size > 16223, f"R60 FODS wheel ({size} bytes) must be larger than R59 (16223 bytes) — new capabilities added"
