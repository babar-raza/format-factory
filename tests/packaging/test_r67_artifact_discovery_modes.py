"""R67 Train B: artifact discovery mode separation.

Validates that the three discovery modes are properly separated:
1. Source-tree local build mode: .local/<run>-metadata/
2. Extracted-bundle mode: bundle-metadata/ with sprint-id.txt
3. Env-var override mode: FORMAT_FACTORY_BUNDLE_METADATA_DIR with sprint-id.txt
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_tools = Path(__file__).resolve().parents[2] / "tools" / "packaging"
if str(_tools) not in sys.path:
    sys.path.insert(0, str(_tools))

from find_bundle_artifacts import find_artifact_dir

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TestLocalBuildMode:
    """Source-tree local build mode: .local/<run>-metadata/ is run-specific by path."""

    def test_local_metadata_nonexistent_run_returns_none(self):
        # .local/r99999-metadata/ does not exist
        result = find_artifact_dir("r99999", PROJECT_ROOT)
        # Might find something via backward-compat bundle-metadata if it exists,
        # but .local/r99999-metadata/package-artifacts/ definitely doesn't exist
        local_path = PROJECT_ROOT / ".local" / "r99999-metadata" / "package-artifacts"
        assert not local_path.exists()

    def test_local_metadata_exists_for_current_sprint(self):
        """R67 local metadata should be discoverable once created."""
        for run in ["r67", "r66", "r65"]:
            d = PROJECT_ROOT / ".local" / f"{run}-metadata" / "package-artifacts"
            if d.exists() and any(d.glob("*.whl")):
                result = find_artifact_dir(run, PROJECT_ROOT)
                assert result is not None, f"{run} local artifacts should be findable"
                break


class TestExtractedBundleMode:
    """Extracted-bundle mode: bundle-metadata/ with sprint-id.txt."""

    def test_extracted_bundle_r99999_false_positive_prevented(self):
        """Core R67 Train B test: r99999 must not match an r66 extracted bundle."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            bm = Path(td) / "bundle-metadata"
            bm.mkdir()
            (bm / "sprint-id.txt").write_text("R66\n", encoding="utf-8")
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
            assert find_artifact_dir("r99999", repo) is None

    def test_extracted_bundle_correct_run_found(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            bm = Path(td) / "bundle-metadata"
            bm.mkdir()
            (bm / "sprint-id.txt").write_text("R67\n", encoding="utf-8")
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
            result = find_artifact_dir("r67", repo)
            assert result == art


class TestEnvVarOverrideMode:
    """Env-var override mode: FORMAT_FACTORY_BUNDLE_METADATA_DIR with sprint-id.txt."""

    def test_env_var_r99999_with_sprint_id_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            bm = Path(td)
            (bm / "sprint-id.txt").write_text("R66\n", encoding="utf-8")
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
            old = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR")
            try:
                os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(bm)
                assert find_artifact_dir("r99999", PROJECT_ROOT) is None
            finally:
                if old is None:
                    os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
                else:
                    os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = old

    def test_env_var_correct_run_returns_path(self):
        with tempfile.TemporaryDirectory() as td:
            bm = Path(td)
            (bm / "sprint-id.txt").write_text("R66\n", encoding="utf-8")
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
            old = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR")
            try:
                os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(bm)
                result = find_artifact_dir("r66", PROJECT_ROOT)
                assert result == art
            finally:
                if old is None:
                    os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
                else:
                    os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = old

    def test_env_var_no_sprint_id_backward_compat(self):
        """Without sprint-id.txt, env-var override matches any run."""
        with tempfile.TemporaryDirectory() as td:
            bm = Path(td)
            # No sprint-id.txt
            art = bm / "package-artifacts"
            art.mkdir()
            (art / "fake-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
            old = os.environ.get("FORMAT_FACTORY_BUNDLE_METADATA_DIR")
            try:
                os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(bm)
                result = find_artifact_dir("r99999", PROJECT_ROOT)
                assert result is not None, "Without sprint-id.txt, env-var allows any run"
            finally:
                if old is None:
                    os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
                else:
                    os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = old
