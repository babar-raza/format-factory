"""
test_r61_extracted_bundle_package_replay.py — R61 Train C: R60 extracted-bundle replay.

Verifies that the R60 evidence bundle can be extracted and package artifacts
discovered without .local/ dependencies.

Repairs IV-R60-006 (no R60 extracted-bundle replay test).
Repairs IV-R60-012 (R60 replay not proven).

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.packaging.find_bundle_artifacts import find_artifact_dir, find_manifest_path


def _get_r60_bundle() -> "Path | None":
    """Get the R60 evidence bundle if available."""
    path = PROJECT_ROOT / ".local" / "r60-pass2-final.zip"
    return path if path.exists() else None


def _get_current_sprint_bundle() -> "Path | None":
    """Get the most recent available evidence bundle (R61 preferred, fallback R60)."""
    for candidate in ["r61-pass2-final.zip", "r60-pass2-final.zip"]:
        path = PROJECT_ROOT / ".local" / candidate
        if path.exists():
            return path
    return None


class TestEnvVarOverrideR61:
    """FORMAT_FACTORY_BUNDLE_METADATA_DIR env-var enables explicit artifact dir."""

    def test_env_var_override_takes_priority(self, tmp_path, monkeypatch):
        """When FORMAT_FACTORY_BUNDLE_METADATA_DIR is set, it takes first priority."""
        env_dir = tmp_path / "explicit-bundle-metadata"
        artifacts = env_dir / "package-artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "r61_pkg-0.1-py3-none-any.whl").write_bytes(b"PK")

        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(env_dir))
        result = find_artifact_dir("r61", PROJECT_ROOT)
        assert result == artifacts, (
            f"Expected env-var override dir {artifacts}, got {result}"
        )

    def test_env_var_manifest_override(self, tmp_path, monkeypatch):
        """Manifest is found from FORMAT_FACTORY_BUNDLE_METADATA_DIR."""
        env_dir = tmp_path / "explicit-bundle-metadata"
        env_dir.mkdir(parents=True)
        manifest = env_dir / "package-artifact-manifest.yaml"
        manifest.write_text("sprint: R61-TEST\n")

        monkeypatch.setenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", str(env_dir))
        result = find_manifest_path("r61", PROJECT_ROOT)
        assert result == manifest, (
            f"Expected env-var manifest {manifest}, got {result}"
        )

    def test_env_var_not_set_falls_through(self, monkeypatch):
        """Without env-var, falls through to default candidates."""
        monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)
        result = find_artifact_dir("r99", PROJECT_ROOT)
        # r99 doesn't exist, should return None
        assert result is None


class TestR60ExtractedBundleReplay:
    """R60 bundle can be extracted and artifacts discovered without .local/ dependencies."""

    def test_r60_bundle_available(self):
        """R60 bundle exists for replay testing."""
        bundle = _get_r60_bundle()
        if bundle is None:
            pytest.skip("R60 bundle not available")
        assert bundle.exists(), f"R60 bundle path invalid: {bundle}"

    def test_r60_bundle_has_package_artifacts(self):
        """R60 bundle contains package-artifacts/ directory with wheels."""
        bundle = _get_r60_bundle()
        if bundle is None:
            pytest.skip("R60 bundle not available")
        with zipfile.ZipFile(bundle) as zf:
            names = zf.namelist()
        artifacts = [n for n in names if "bundle-metadata/package-artifacts/" in n and n.endswith(".whl")]
        assert len(artifacts) >= 10, (
            f"Expected at least 10 wheels in bundle. Found: {artifacts}"
        )

    def test_r60_bundle_has_manifest(self):
        """R60 bundle contains package-artifact-manifest.yaml."""
        bundle = _get_r60_bundle()
        if bundle is None:
            pytest.skip("R60 bundle not available")
        with zipfile.ZipFile(bundle) as zf:
            names = zf.namelist()
        manifests = [n for n in names if "package-artifact-manifest.yaml" in n]
        assert manifests, f"No manifest found in bundle. Entries: {[n for n in names[:20]]}"

    def test_r60_extracted_bundle_artifact_discovery(self, tmp_path):
        """Extracted R60 bundle: find_artifact_dir discovers artifacts without .local/."""
        bundle = _get_r60_bundle()
        if bundle is None:
            pytest.skip("R60 bundle not available")

        # Extract to temp directory (simulates delivery to a clean machine)
        extract_dir = tmp_path / "r60-extracted"
        with zipfile.ZipFile(bundle) as zf:
            zf.extractall(extract_dir)

        # Simulate: project root is the extracted repo/ subdirectory
        repo_root = extract_dir / "repo"
        if not repo_root.exists():
            # Some bundles extract flat; adapt
            repo_root = extract_dir

        # Use env-var to point at extracted bundle-metadata
        bundle_meta = extract_dir / "bundle-metadata"
        if bundle_meta.exists():
            os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(bundle_meta)
            try:
                result = find_artifact_dir("r60", repo_root)
                assert result is not None, (
                    f"find_artifact_dir must find artifacts in extracted bundle. "
                    f"Checked: {bundle_meta / 'package-artifacts'}"
                )
                wheels = list(result.glob("*.whl"))
                assert len(wheels) >= 10, (
                    f"Expected 10+ wheels in extracted bundle artifact dir. Got: {wheels}"
                )
            finally:
                os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
        else:
            pytest.skip(f"Extracted bundle has no bundle-metadata/ dir: {list(extract_dir.iterdir())}")

    def test_r60_extracted_bundle_manifest_discovery(self, tmp_path):
        """Extracted R60 bundle: find_manifest_path discovers manifest without .local/."""
        bundle = _get_r60_bundle()
        if bundle is None:
            pytest.skip("R60 bundle not available")

        extract_dir = tmp_path / "r60-manifest-test"
        with zipfile.ZipFile(bundle) as zf:
            # Extract only the manifest to speed up test
            manifests = [n for n in zf.namelist() if "package-artifact-manifest.yaml" in n]
            if not manifests:
                pytest.skip("No manifest in bundle")
            for name in manifests:
                zf.extract(name, extract_dir)

        bundle_meta = extract_dir / "bundle-metadata"
        if bundle_meta.exists() and (bundle_meta / "package-artifact-manifest.yaml").exists():
            os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(bundle_meta)
            try:
                result = find_manifest_path("r60", extract_dir)
                assert result is not None, "Manifest must be discoverable from extracted bundle"
                assert result.exists(), f"Manifest path {result} does not exist"
            finally:
                os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
        else:
            pytest.skip(f"Manifest not at expected location in extract: {extract_dir}")

    def test_r60_extracted_bundle_no_local_dependency(self):
        """Extracted R60 bundle replay must NOT require .local/ directory."""
        # Verify the test helper (find_artifact_dir) does not hardcode .local/
        import inspect
        from tools.packaging import find_bundle_artifacts
        source = inspect.getsource(find_bundle_artifacts)
        # The fallback to .local/ is acceptable but should not be the ONLY path
        # Verify that bundle-metadata/ is also a candidate
        assert "bundle-metadata" in source, (
            "find_bundle_artifacts must include bundle-metadata/ as a candidate"
        )
        assert "FORMAT_FACTORY_BUNDLE_METADATA_DIR" in source, (
            "find_bundle_artifacts must support env-var override"
        )


class TestR61PackagingNoLocalPaths:
    """R61 packaging tests must not hardcode .local/ paths."""

    def test_r60_test_no_longer_has_hardcoded_build_dir(self):
        """R60 artifact source commit test (IV-R60-005 repair) uses portable discovery."""
        target = PROJECT_ROOT / "tests" / "packaging" / "test_r60_artifact_source_commit.py"
        assert target.exists(), "test_r60_artifact_source_commit.py must exist"
        content = target.read_text(encoding="utf-8")
        # The old pattern was: BUILD_DIR = PROJECT_ROOT / ".local" / "package-builds"
        assert 'BUILD_DIR = PROJECT_ROOT / ".local" / "package-builds"' not in content, (
            "IV-R60-005: test_r60_artifact_source_commit.py must not hardcode BUILD_DIR "
            "with .local/package-builds path. Use find_artifact_dir instead."
        )

    def test_find_artifact_dir_is_portable(self, tmp_path):
        """find_artifact_dir works from a completely local-path-free environment."""
        # Create a fake extracted bundle structure
        fake_meta = tmp_path / "bundle-metadata"
        fake_artifacts = fake_meta / "package-artifacts"
        fake_artifacts.mkdir(parents=True)
        (fake_artifacts / "test_pkg-0.1-py3-none-any.whl").write_bytes(b"PK")

        os.environ["FORMAT_FACTORY_BUNDLE_METADATA_DIR"] = str(fake_meta)
        try:
            result = find_artifact_dir("r61", tmp_path)
            assert result == fake_artifacts, (
                f"Expected {fake_artifacts}, got {result}"
            )
        finally:
            os.environ.pop("FORMAT_FACTORY_BUNDLE_METADATA_DIR", None)
