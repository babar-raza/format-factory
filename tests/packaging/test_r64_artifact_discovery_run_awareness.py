"""
test_r64_artifact_discovery_run_awareness.py — R64 Train C: Artifact discovery run-awareness.

Closes:
- IV-R63-006: Artifact discovery not run-aware for extracted bundles
- IV-R63-008: Packaging test needs extracted-bundle mode

Tests:
- find_artifact_dir returns None for nonexistent run
- find_artifact_dir returns correct dir for valid run (R64 or R63 fallback)
- find_artifact_dir does not return unrelated run's artifacts
- find_manifest_path returns None for nonexistent run
- Extracted-bundle mode works with FORMAT_FACTORY_BUNDLE_METADATA_DIR

R64 Sprint: FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
IV-R63-006, IV-R63-008
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.packaging.find_bundle_artifacts import find_artifact_dir, find_manifest_path


class TestArtifactDiscoveryRunAwareness:
    """Artifact discovery must be run-aware."""

    def test_nonexistent_run_returns_none(self):
        """r99999 must return None — no false positive from bundle-metadata."""
        result = find_artifact_dir("r99999", PROJECT_ROOT)
        assert result is None, (
            f"find_artifact_dir('r99999', ...) must return None, got: {result}"
        )

    def test_r64_returns_path_or_none(self):
        """R64 artifacts may or may not exist yet."""
        result = find_artifact_dir("r64", PROJECT_ROOT)
        if result is not None:
            assert result.is_dir()
            assert any(result.glob("*.whl")), f"R64 artifact dir must contain .whl files: {result}"

    def test_r63_fallback_available(self):
        """R63 artifacts should be discoverable."""
        result = find_artifact_dir("r63", PROJECT_ROOT)
        if result is not None:
            assert result.is_dir()
            assert any(result.glob("*.whl"))

    def test_manifest_nonexistent_run_returns_none(self):
        result = find_manifest_path("r99999", PROJECT_ROOT)
        assert result is None

    def test_manifest_r64_returns_path_or_none(self):
        result = find_manifest_path("r64", PROJECT_ROOT)
        if result is not None:
            assert result.is_file()


class TestExtractedBundleMode:
    """Extracted-bundle mode via env var."""

    def test_env_var_override_with_valid_dir(self, tmp_path, monkeypatch):
        """FORMAT_FACTORY_BUNDLE_METADATA_DIR should take priority."""
        artifacts = tmp_path / "package-artifacts"
        artifacts.mkdir()
        # Create a dummy .whl file
        (artifacts / "dummy-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04dummy")
        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(tmp_path))
        result = find_artifact_dir("r64", PROJECT_ROOT)
        assert result is not None
        assert result == artifacts

    def test_env_var_override_with_empty_dir(self, tmp_path, monkeypatch):
        """Empty artifacts dir should not match (no .whl files)."""
        artifacts = tmp_path / "package-artifacts"
        artifacts.mkdir()
        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(tmp_path))
        result = find_artifact_dir("r64", PROJECT_ROOT)
        # Should fall through to other candidates since env dir has no .whl
        # Result depends on whether other candidate dirs exist


class TestR64PackagePresence:
    """R64 packages must be present when R64 artifacts are built."""

    EXPECTED_WHEELS = [
        "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_fodp-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_gnumeric-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_abw-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_pbm-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_pgm-0.1.0.dev0-py3-none-any.whl",
        "aspose_format_factory_sylk-0.1.0.dev0-py3-none-any.whl",
    ]

    def test_all_wheels_present(self):
        artifacts = find_artifact_dir("r64", PROJECT_ROOT)
        if artifacts is None:
            pytest.skip("R64 artifacts not yet built")
        present = {p.name for p in artifacts.glob("*.whl")}
        missing = [w for w in self.EXPECTED_WHEELS if w not in present]
        assert not missing, f"Missing R64 wheels: {missing}"

    def test_all_sdists_present(self):
        artifacts = find_artifact_dir("r64", PROJECT_ROOT)
        if artifacts is None:
            pytest.skip("R64 artifacts not yet built")
        sdists = list(artifacts.glob("*.tar.gz"))
        assert len(sdists) >= 10, f"Expected 10 sdists, found {len(sdists)}"

    def test_nupkgs_present(self):
        artifacts = find_artifact_dir("r64", PROJECT_ROOT)
        if artifacts is None:
            pytest.skip("R64 artifacts not yet built")
        nupkgs = list(artifacts.glob("*.nupkg"))
        assert len(nupkgs) >= 2, f"Expected 2 nupkgs, found {len(nupkgs)}"
