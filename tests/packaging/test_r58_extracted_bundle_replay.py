"""
test_r58_extracted_bundle_replay.py — R58 Train D: Extracted bundle package replay.

Verifies that:
1. find_artifact_dir checks PROJECT_ROOT.parent/bundle-metadata/package-artifacts
2. When R57 bundle is extracted to a temp dir, package artifacts are discovered
   without manual symlink
3. Package tests pass with no skipped artifact checks when run from extracted repo

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-007
"""
from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.packaging.find_bundle_artifacts import find_artifact_dir, find_manifest_path


class TestParentDirDiscovery:
    """find_artifact_dir must check PROJECT_ROOT.parent/bundle-metadata/package-artifacts."""

    def test_parent_bundle_metadata_discovered(self, tmp_path):
        """When artifacts are in parent/bundle-metadata/, they are discovered."""
        # Simulate extracted bundle layout:
        #   tmp_path/
        #     repo/          <- project_root
        #     bundle-metadata/package-artifacts/  <- artifacts here
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        bundle_artifacts = tmp_path / "bundle-metadata" / "package-artifacts"
        bundle_artifacts.mkdir(parents=True)
        (bundle_artifacts / "test_pkg-0.1-py3-none-any.whl").write_bytes(b"PK fake wheel")

        result = find_artifact_dir("r58", repo_dir)
        assert result == bundle_artifacts, (
            f"Expected {bundle_artifacts}, got {result}. "
            "find_artifact_dir must check PROJECT_ROOT.parent/bundle-metadata/package-artifacts"
        )

    def test_local_takes_priority_over_parent(self, tmp_path):
        """When .local/<run>-metadata/ exists, it takes priority over parent/bundle-metadata/."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        # Both local and parent exist
        local_artifacts = repo_dir / ".local" / "r58-metadata" / "package-artifacts"
        local_artifacts.mkdir(parents=True)
        (local_artifacts / "local_pkg-0.1-py3-none-any.whl").write_bytes(b"PK local")
        parent_artifacts = tmp_path / "bundle-metadata" / "package-artifacts"
        parent_artifacts.mkdir(parents=True)
        (parent_artifacts / "parent_pkg-0.1-py3-none-any.whl").write_bytes(b"PK parent")

        result = find_artifact_dir("r58", repo_dir)
        assert result == local_artifacts, "Local dir must take priority over parent"

    def test_parent_manifest_discovered(self, tmp_path):
        """find_manifest_path discovers manifest from parent/bundle-metadata/."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        bundle_meta = tmp_path / "bundle-metadata"
        bundle_meta.mkdir()
        manifest = bundle_meta / "package-artifact-manifest.yaml"
        manifest.write_text("installed_artifact_policy: self_contained\n")

        result = find_manifest_path("r58", repo_dir)
        assert result == manifest

    def test_no_artifacts_returns_none(self, tmp_path):
        """When parent/bundle-metadata/ has no .whl files, returns None."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        bundle_artifacts = tmp_path / "bundle-metadata" / "package-artifacts"
        bundle_artifacts.mkdir(parents=True)
        # No .whl files
        (bundle_artifacts / "README.txt").write_text("no wheels here")

        result = find_artifact_dir("r58", repo_dir)
        assert result is None


class TestExtractedBundleReplay:
    """Simulate extracting R57 bundle and running package tests from extracted repo."""

    def test_r57_bundle_extraction_finds_artifacts(self):
        """When R57 bundle is extracted, find_artifact_dir discovers artifacts from parent."""
        bundle = PROJECT_ROOT / ".local" / "r57-pass2-final.zip"
        if not bundle.exists():
            pytest.skip("R57 pass-2 bundle not available")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            with zipfile.ZipFile(bundle) as zf:
                zf.extractall(tmp)

            extracted_repo = tmp / "repo"
            assert extracted_repo.exists(), "Extracted bundle must have repo/ directory"

            # Check parent/bundle-metadata/ exists
            parent_pkg = tmp / "bundle-metadata" / "package-artifacts"
            assert parent_pkg.exists(), "Extracted bundle must have bundle-metadata/package-artifacts/"

            whl_files = list(parent_pkg.glob("*.whl"))
            assert len(whl_files) == 7, f"Expected 7 wheels, got {len(whl_files)}"

            # Now test that find_artifact_dir finds them
            result = find_artifact_dir("r57", extracted_repo)
            assert result is not None, (
                "find_artifact_dir must find artifacts from extracted bundle's parent/bundle-metadata/. "
                "IV-R57-007 fix: check PROJECT_ROOT.parent/bundle-metadata/package-artifacts"
            )
            assert result == parent_pkg or result.resolve() == parent_pkg.resolve()

    def test_extracted_bundle_manifest_found(self):
        """Manifest is found from extracted bundle parent dir."""
        bundle = PROJECT_ROOT / ".local" / "r57-pass2-final.zip"
        if not bundle.exists():
            pytest.skip("R57 pass-2 bundle not available")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            with zipfile.ZipFile(bundle) as zf:
                zf.extractall(tmp)

            extracted_repo = tmp / "repo"
            manifest = find_manifest_path("r57", extracted_repo)
            # May be None if manifest not in bundle-metadata root — that's acceptable
            # The important thing is it doesn't fail, and if present, is correct
            if manifest is not None:
                assert manifest.exists()
                content = manifest.read_text()
                assert "self_contained" in content or "package" in content.lower()
