"""R67 Train B: artifact discovery must return None for nonexistent runs in all modes.

Covers IV-R67-001: bundle-metadata/ fallback paths now require sprint-id.txt match,
preventing false positives in extracted-bundle mode.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_tools = Path(__file__).resolve().parents[2] / "tools" / "packaging"
if str(_tools) not in sys.path:
    sys.path.insert(0, str(_tools))

import pytest
from find_bundle_artifacts import find_artifact_dir, find_manifest_path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TestNoFalsePositiveWithoutEnv:
    """Without env var, nonexistent runs must return None."""

    def test_r99999_artifact_dir_none(self):
        assert find_artifact_dir("r99999", PROJECT_ROOT) is None

    def test_r99999_manifest_path_none(self):
        assert find_manifest_path("r99999", PROJECT_ROOT) is None

    def test_r00000_artifact_dir_none(self):
        assert find_artifact_dir("r00000", PROJECT_ROOT) is None

    def test_r00000_manifest_path_none(self):
        assert find_manifest_path("r00000", PROJECT_ROOT) is None


class TestNoFalsePositiveWithEnv:
    """With env var pointing to real metadata, nonexistent runs must return None."""

    def _get_metadata_dir(self):
        for run in ["r67", "r66", "r65"]:
            d = PROJECT_ROOT / ".local" / f"{run}-metadata"
            if d.exists():
                return d
        pytest.skip("No metadata directory available")

    def test_r99999_with_env_returns_none(self):
        d = self._get_metadata_dir()
        old = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR")
        try:
            os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(d)
            assert find_artifact_dir("r99999", PROJECT_ROOT) is None
        finally:
            if old is None:
                os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
            else:
                os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = old

    def test_r99999_manifest_with_env_returns_none(self):
        d = self._get_metadata_dir()
        old = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR")
        try:
            os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(d)
            assert find_manifest_path("r99999", PROJECT_ROOT) is None
        finally:
            if old is None:
                os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
            else:
                os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = old

    def test_correct_run_with_env_finds_artifacts(self):
        d = self._get_metadata_dir()
        # Derive run label from directory name
        run = d.name.replace("-metadata", "")
        old = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR")
        try:
            os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(d)
            result = find_artifact_dir(run, PROJECT_ROOT)
            if (d / "package-artifacts").exists():
                assert result is not None
        finally:
            if old is None:
                os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
            else:
                os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = old


class TestExtractedBundleModeWithSprintId:
    """Simulate extracted-bundle mode: bundle-metadata/ with sprint-id.txt."""

    def test_wrong_run_returns_none_when_sprint_id_present(self):
        """In extracted-bundle mode, r99999 must not match bundle-metadata/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_root = Path(tmpdir) / "repo"
            fake_root.mkdir()
            bm = Path(tmpdir) / "bundle-metadata"
            bm.mkdir()
            # Create sprint-id.txt for r66
            (bm / "sprint-id.txt").write_text("FORMAT-FACTORY-R66-...\nR66\n", encoding="utf-8")
            # Create package-artifacts with a wheel
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")

            # From extracted repo root, r99999 must NOT match
            result = find_artifact_dir("r99999", fake_root)
            assert result is None, "r99999 must not match extracted r66 bundle"

    def test_correct_run_finds_artifacts_when_sprint_id_present(self):
        """In extracted-bundle mode, r66 should match bundle-metadata/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_root = Path(tmpdir) / "repo"
            fake_root.mkdir()
            bm = Path(tmpdir) / "bundle-metadata"
            bm.mkdir()
            (bm / "sprint-id.txt").write_text("FORMAT-FACTORY-R66-...\nR66\n", encoding="utf-8")
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")

            result = find_artifact_dir("r66", fake_root)
            assert result == art, f"r66 should find extracted bundle artifacts, got {result}"

    def test_no_sprint_id_backward_compat(self):
        """Without sprint-id.txt, bundle-metadata/ is returned for any run (backward compat)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_root = Path(tmpdir) / "repo"
            fake_root.mkdir()
            bm = Path(tmpdir) / "bundle-metadata"
            bm.mkdir()
            # No sprint-id.txt
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")

            result = find_artifact_dir("r99999", fake_root)
            assert result is not None, "Without sprint-id.txt, backward-compat allows any run"
