"""
test_r59_artifact_discovery_modes.py — R59 Train D: Artifact discovery mode normalization.

Verifies:
1. Local dev mode (default): .local/<run>-metadata/
2. Extracted bundle mode: parent/bundle-metadata/ (via parent-dir fix)
3. Env-var override mode: FORMAT_FACTORY_BUNDLE_METADATA_DIR
4. Legacy R55/R56/R57 tests do not affect current RC validation (isolation)
5. Priority ordering: env-var > local-dev > in-tree-extracted > parent-extracted > legacy

R59 Sprint: FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R58-009
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.packaging.find_bundle_artifacts import find_artifact_dir, find_manifest_path


class TestDiscoveryPriority:
    """Strict priority: env-var > local-dev > in-tree > parent-extracted > legacy."""

    def test_env_var_beats_local_dev(self, tmp_path, monkeypatch):
        root = tmp_path / "repo"
        root.mkdir()
        # Local dev exists
        local = root / ".local" / "r59-metadata" / "package-artifacts"
        local.mkdir(parents=True)
        (local / "local.whl").write_bytes(b"PK")
        # Env var also set
        env = tmp_path / "env-meta" / "package-artifacts"
        env.mkdir(parents=True)
        (env / "env.whl").write_bytes(b"PK")
        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(env.parent))
        assert find_artifact_dir("r59", root) == env

    def test_local_dev_beats_extracted(self, tmp_path, monkeypatch):
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        root = tmp_path / "repo"
        root.mkdir()
        # Both local dev and extracted present
        local = root / ".local" / "r59-metadata" / "package-artifacts"
        local.mkdir(parents=True)
        (local / "local.whl").write_bytes(b"PK")
        parent = tmp_path / "bundle-metadata" / "package-artifacts"
        parent.mkdir(parents=True)
        (parent / "extracted.whl").write_bytes(b"PK")
        assert find_artifact_dir("r59", root) == local

    def test_extracted_parent_beats_legacy(self, tmp_path, monkeypatch):
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        root = tmp_path / "repo"
        root.mkdir()
        # Only extracted parent
        parent = tmp_path / "bundle-metadata" / "package-artifacts"
        parent.mkdir(parents=True)
        (parent / "extracted.whl").write_bytes(b"PK")
        assert find_artifact_dir("r59", root) == parent

    def test_none_when_nothing_found(self, tmp_path, monkeypatch):
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        root = tmp_path / "repo"
        root.mkdir()
        assert find_artifact_dir("r99", root) is None


class TestManifestDiscovery:
    """Manifest discovery follows same priority as artifacts."""

    def test_env_var_manifest(self, tmp_path, monkeypatch):
        env = tmp_path / "env-meta"
        env.mkdir()
        (env / "package-artifact-manifest.yaml").write_text("installed_artifact_policy: self_contained\n")
        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(env))
        result = find_manifest_path("r59", tmp_path / "repo")
        assert result == env / "package-artifact-manifest.yaml"

    def test_local_dev_manifest(self, tmp_path, monkeypatch):
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        root = tmp_path / "repo"
        root.mkdir()
        local_meta = root / ".local" / "r59-metadata"
        local_meta.mkdir(parents=True)
        manifest = local_meta / "package-artifact-manifest.yaml"
        manifest.write_text("installed_artifact_policy: self_contained\n")
        assert find_manifest_path("r59", root) == manifest

    def test_none_when_no_manifest(self, tmp_path, monkeypatch):
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        root = tmp_path / "repo"
        root.mkdir()
        assert find_manifest_path("r99", root) is None


class TestLegacyIsolation:
    """Legacy R55/R56/R57 tests use specific run_number; they cannot interfere with R59."""

    def test_different_run_numbers_are_independent(self, tmp_path, monkeypatch):
        """R55 artifacts in .local/r55-metadata do NOT appear when querying R59."""
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        root = tmp_path / "repo"
        root.mkdir()
        # R55 artifacts
        r55 = root / ".local" / "r55-metadata" / "package-artifacts"
        r55.mkdir(parents=True)
        (r55 / "r55_pkg.whl").write_bytes(b"PK")
        # R59 query → should NOT find r55 artifacts
        result = find_artifact_dir("r59", root)
        assert result is None, (
            f"R59 query must not find R55 artifacts, got: {result}"
        )

    def test_r59_artifacts_not_found_by_r55_query(self, tmp_path, monkeypatch):
        """R59 artifacts are not visible when querying for R55."""
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        root = tmp_path / "repo"
        root.mkdir()
        # R59 artifacts in local
        r59 = root / ".local" / "r59-metadata" / "package-artifacts"
        r59.mkdir(parents=True)
        (r59 / "r59_pkg.whl").write_bytes(b"PK")
        # R55 query → should NOT find r59 artifacts
        result = find_artifact_dir("r55", root)
        assert result is None, (
            f"R55 query must not find R59 artifacts, got: {result}"
        )
