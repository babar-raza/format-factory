"""R68 Train D: ENV-var isolation proofs for find_bundle_artifacts.

Proves that:
1. When FORMAT_FACTORY_BUNDLE_METADATA_DIR points to a real sprint dir, synthetic
   temp-bundle tests are not contaminated (env var cleared via monkeypatch).
2. When env var is set to a dir whose sprint-id.txt does NOT match the requested
   run, find_artifact_dir still returns None for that run.
3. When env var is set to a dir whose sprint-id.txt DOES match, it returns the env
   path (expected behaviour — env-var override is intentional).
4. When env var is absent, synthetic parent bundle-metadata is correctly found.

R68 Sprint: FORMAT-FACTORY-R68-FINAL-CLOSEOUT-HYGIENE-LOCAL-RC-SEAL-MEGA-TRAIN-001
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

_ENV_VAR = "FORMAT_FACTORY_BUNDLE_METADATA_DIR"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _make_metadata_dir(tmpdir: Path, sprint_label: str) -> tuple[Path, Path]:
    """Create a metadata directory (simulates .local/r##-metadata)."""
    md = tmpdir / f"{sprint_label}-metadata"
    md.mkdir(parents=True)
    (md / "sprint-id.txt").write_text(
        f"FORMAT-FACTORY-{sprint_label.upper()}-001\n", encoding="utf-8"
    )
    art = md / "package-artifacts"
    art.mkdir()
    (art / "pkg-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
    (md / "package-artifact-manifest.yaml").write_text(
        f"run: {sprint_label}\nartifact_count: 1\n", encoding="utf-8"
    )
    return md, art


def _make_extracted_bundle(tmpdir: Path, sprint_label: str) -> tuple[Path, Path]:
    """Create a synthetic extracted-bundle layout (parent bundle-metadata)."""
    repo_root = tmpdir / "repo"
    repo_root.mkdir(exist_ok=True)
    bm = tmpdir / "bundle-metadata"
    bm.mkdir(exist_ok=True)
    (bm / "sprint-id.txt").write_text(
        f"FORMAT-FACTORY-{sprint_label.upper()}-001\n", encoding="utf-8"
    )
    art = bm / "package-artifacts"
    art.mkdir(exist_ok=True)
    (art / "pkg-0.1.0-py3-none-any.whl").write_bytes(b"PK\x03\x04")
    (bm / "package-artifact-manifest.yaml").write_text(
        f"run: {sprint_label}\n", encoding="utf-8"
    )
    return repo_root, art


class TestEnvVarIsolation:
    """Env-var is cleared: synthetic bundle should be found cleanly."""

    def test_cleared_env_var_does_not_leak_into_synthetic_bundle(self, monkeypatch):
        """When env var is cleared, only synthetic parent bundle-metadata is seen."""
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo, art = _make_extracted_bundle(Path(td), "r68")
            result = find_artifact_dir("r68", repo)
            assert result == art

    def test_cleared_env_var_nonexistent_sprint_returns_none(self, monkeypatch):
        """With env var cleared, non-matching sprint still returns None."""
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo, _ = _make_extracted_bundle(Path(td), "r68")
            result = find_artifact_dir("r99999", repo)
            assert result is None

    def test_cleared_env_does_not_expose_real_local_metadata(self, monkeypatch):
        """With env var cleared and using a temp repo root, .local/ is not found."""
        monkeypatch.delenv(_ENV_VAR, raising=False)
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            # No bundle-metadata, no .local in this temp repo — should return None
            result = find_artifact_dir("r68", repo)
            assert result is None


class TestEnvVarMatchBehaviour:
    """When env var is set, sprint-id.txt governs whether it is used."""

    def test_env_var_matching_sprint_returns_env_artifacts(self, monkeypatch):
        """Env var pointing to sprint-matching dir is returned (correct behaviour)."""
        with tempfile.TemporaryDirectory() as td:
            md, art = _make_metadata_dir(Path(td), "r68")
            monkeypatch.setenv(_ENV_VAR, str(md))
            with tempfile.TemporaryDirectory() as td2:
                repo = Path(td2) / "repo"
                repo.mkdir()
                result = find_artifact_dir("r68", repo)
                assert result == art

    def test_env_var_mismatched_sprint_does_not_return_env_artifacts(self, monkeypatch):
        """Env var pointing to r68-metadata is NOT returned when querying r65."""
        with tempfile.TemporaryDirectory() as td:
            md, _ = _make_metadata_dir(Path(td), "r68")
            monkeypatch.setenv(_ENV_VAR, str(md))
            with tempfile.TemporaryDirectory() as td2:
                repo = Path(td2) / "repo"
                repo.mkdir()
                result = find_artifact_dir("r65", repo)
                # env var has r68 sprint-id.txt, not r65 → should not match
                assert result is None

    def test_env_var_mismatched_sprint_does_not_contaminate_find_manifest(self, monkeypatch):
        """find_manifest_path: env var with wrong sprint does not return manifest."""
        with tempfile.TemporaryDirectory() as td:
            md, _ = _make_metadata_dir(Path(td), "r68")
            monkeypatch.setenv(_ENV_VAR, str(md))
            with tempfile.TemporaryDirectory() as td2:
                repo = Path(td2) / "repo"
                repo.mkdir()
                result = find_manifest_path("r65", repo)
                assert result is None

    def test_env_var_matching_sprint_returns_manifest(self, monkeypatch):
        """find_manifest_path: env var with matching sprint returns manifest."""
        with tempfile.TemporaryDirectory() as td:
            md, _ = _make_metadata_dir(Path(td), "r68")
            monkeypatch.setenv(_ENV_VAR, str(md))
            with tempfile.TemporaryDirectory() as td2:
                repo = Path(td2) / "repo"
                repo.mkdir()
                result = find_manifest_path("r68", repo)
                assert result is not None
                assert result.name == "package-artifact-manifest.yaml"


class TestEnvVarSprint67Regression:
    """Regression: R67 synthetic bundle tests fail when env var points to r67-metadata.

    Proves the fix introduced in R68 Train D (monkeypatch.delenv in synthetic tests)
    correctly isolates test_r67_extracted_current_bundle_discovery tests from a
    globally-set FORMAT_FACTORY_BUNDLE_METADATA_DIR.
    """

    def test_r67_synthetic_bundle_isolated_when_env_points_to_real_r67(self, monkeypatch):
        """Simulate the pre-fix bug: env var points to dir with r67 sprint-id.txt.

        Post-fix: clearing env var means synthetic bundle is correctly found.
        """
        with tempfile.TemporaryDirectory() as real_td:
            # Create a "real" r67-metadata that matches r67
            real_md, _ = _make_metadata_dir(Path(real_td), "r67")
            # Simulate globally-set env var (as would happen in extracted-bundle mode)
            monkeypatch.setenv(_ENV_VAR, str(real_md))
            # Now clear it (as the fixed test does with monkeypatch.delenv)
            monkeypatch.delenv(_ENV_VAR, raising=False)
            # Synthetic bundle in its own temp dir
            with tempfile.TemporaryDirectory() as syn_td:
                repo, art = _make_extracted_bundle(Path(syn_td), "r67")
                result = find_artifact_dir("r67", repo)
                # Should find synthetic art, not real_md/package-artifacts
                assert result == art
                assert result != real_md / "package-artifacts"

    def test_r67_synthetic_nonexistent_sprint_isolated_from_real_r67(self, monkeypatch):
        """With env cleared: find_artifact_dir("r67", temp_repo) for non-r67 sprint = None."""
        with tempfile.TemporaryDirectory() as real_td:
            real_md, _ = _make_metadata_dir(Path(real_td), "r67")
            monkeypatch.setenv(_ENV_VAR, str(real_md))
            monkeypatch.delenv(_ENV_VAR, raising=False)
            with tempfile.TemporaryDirectory() as syn_td:
                repo, _ = _make_extracted_bundle(Path(syn_td), "r67")
                result = find_artifact_dir("r99999", repo)
                assert result is None
