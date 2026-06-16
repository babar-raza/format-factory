"""R66 Train D: artifact discovery must not return false positives for nonexistent runs."""

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


class TestNoFalsePositiveWithEnv:
    """With env var pointing to real metadata, nonexistent runs must return None."""

    def _get_metadata_dir(self):
        d = PROJECT_ROOT / ".local" / "r66-metadata"
        if not d.exists():
            d = PROJECT_ROOT / ".local" / "r65-metadata"
        if not d.exists():
            pytest.skip("No metadata directory available")
        return d

    def test_r99999_with_env_returns_none(self, monkeypatch):
        d = self._get_metadata_dir()
        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(d))
        assert find_artifact_dir("r99999", PROJECT_ROOT) is None

    def test_r99999_manifest_with_env_returns_none(self, monkeypatch):
        d = self._get_metadata_dir()
        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(d))
        assert find_manifest_path("r99999", PROJECT_ROOT) is None

    def test_correct_run_with_env_finds_artifacts(self, monkeypatch):
        d = self._get_metadata_dir()
        run = "r66" if "r66" in str(d) else "r65"
        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(d))
        result = find_artifact_dir(run, PROJECT_ROOT)
        if (d / "package-artifacts").exists():
            assert result is not None


class TestEnvVarWithNoSprintId:
    """Env var override without sprint-id.txt should still work (backward compat)."""

    def test_no_sprint_id_allows_any_run(self, monkeypatch):
        with tempfile.TemporaryDirectory() as tmpdir:
            art_dir = Path(tmpdir) / "package-artifacts"
            art_dir.mkdir()
            (art_dir / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
            monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", tmpdir)
            result = find_artifact_dir("r99999", PROJECT_ROOT)
            assert result is not None, "Without sprint-id.txt, any run should match"
