"""
test_r57_package_rc.py — R57 Train C: Package RC Replay from Extracted Bundle.

Fixes IV-R56-005: test_r56_package_rc.py used a hardcoded .local/r56-metadata path.
This test uses find_artifact_dir() for portable discovery, skipping gracefully
when artifacts are not available (clean git clone, CI, extracted-bundle-only environments).

Also validates:
- All 7 expected R57 wheels present when artifacts dir is available
- FODT wheel contains R56+ hyperlink and nested list code
- Package manifest uses correct SHA-256 (64-char, not 32-char MD5)
- Package manifest self_contained policy

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
IV-R56-005
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.packaging.find_bundle_artifacts import find_artifact_dir, find_manifest_path

# Use discovery instead of hardcoded path
ARTIFACTS_DIR = find_artifact_dir("r57", PROJECT_ROOT)
MANIFEST_PATH = find_manifest_path("r57", PROJECT_ROOT)

# Fall back to R56 artifacts if R57 not yet built (supports running mid-sprint)
if ARTIFACTS_DIR is None:
    ARTIFACTS_DIR = find_artifact_dir("r56", PROJECT_ROOT)
if MANIFEST_PATH is None:
    MANIFEST_PATH = find_manifest_path("r56", PROJECT_ROOT)

EXPECTED_WHEELS = [
    "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_fodp-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_gnumeric-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_abw-0.1.0.dev0-py3-none-any.whl",
]


def _skip_if_no_artifacts():
    """Skip test if artifact directory is not available."""
    if ARTIFACTS_DIR is None:
        pytest.skip("Package artifacts not available in this environment (no .local/ dir, no bundle-metadata/)")


class TestDiscoveryFunction:
    """find_artifact_dir must discover artifacts portably."""

    def test_discovery_returns_none_for_nonexistent_run(self):
        result = find_artifact_dir("r99999", PROJECT_ROOT)
        assert result is None

    def test_discovery_returns_path_or_none(self):
        result = find_artifact_dir("r57", PROJECT_ROOT)
        if result is not None:
            assert result.is_dir()
            assert any(result.glob("*.whl"))

    def test_discovery_checks_local_dir_first(self, tmp_path):
        """When .local/<run>-metadata/package-artifacts/ exists with .whl, it is returned first."""
        local_artifacts = tmp_path / ".local" / "r99-metadata" / "package-artifacts"
        local_artifacts.mkdir(parents=True)
        (local_artifacts / "test_pkg-0.1-py3-none-any.whl").write_bytes(b"PK fake")
        result = find_artifact_dir("r99", tmp_path)
        assert result == local_artifacts

    def test_discovery_falls_back_to_bundle_metadata(self, tmp_path):
        """When .local/ has no .whl but bundle-metadata/ does, bundle-metadata is returned."""
        bundle_artifacts = tmp_path / "bundle-metadata" / "package-artifacts"
        bundle_artifacts.mkdir(parents=True)
        (bundle_artifacts / "test_pkg-0.1-py3-none-any.whl").write_bytes(b"PK fake")
        result = find_artifact_dir("r99", tmp_path)
        assert result == bundle_artifacts

    def test_find_manifest_returns_none_for_nonexistent_run(self):
        result = find_manifest_path("r99999", PROJECT_ROOT)
        assert result is None


class TestPackageArtifactsExist:
    """All 7 wheel artifacts must be present when artifact dir is available."""

    def test_artifacts_dir_discovered(self):
        _skip_if_no_artifacts()
        assert ARTIFACTS_DIR is not None

    @pytest.mark.parametrize("wheel_name", EXPECTED_WHEELS)
    def test_wheel_file_exists(self, wheel_name):
        _skip_if_no_artifacts()
        whl = ARTIFACTS_DIR / wheel_name
        assert whl.exists(), f"Wheel missing: {whl}"

    @pytest.mark.parametrize("wheel_name", EXPECTED_WHEELS)
    def test_wheel_file_nonzero(self, wheel_name):
        _skip_if_no_artifacts()
        whl = ARTIFACTS_DIR / wheel_name
        if whl.exists():
            assert whl.stat().st_size > 1000, f"Wheel suspiciously small: {whl}"

    def test_all_seven_wheels_present(self):
        _skip_if_no_artifacts()
        present = [w for w in EXPECTED_WHEELS if (ARTIFACTS_DIR / w).exists()]
        assert len(present) == 7, f"Expected 7 wheels, found {len(present)}"


class TestWheelContents:
    """Wheel contents must include R56+ source changes."""

    def test_fodt_wheel_has_hyperlink_code(self):
        _skip_if_no_artifacts()
        whl = ARTIFACTS_DIR / "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl"
        if not whl.exists():
            pytest.skip("FODT wheel not present")
        with zipfile.ZipFile(whl, "r") as zf:
            writer_names = [n for n in zf.namelist() if "writer.py" in n]
            assert writer_names, "writer.py not found in FODT wheel"
            src = zf.read(writer_names[0]).decode("utf-8")
        assert "xlink" in src, "writer.py missing xlink namespace (R56 hyperlink code)"

    def test_fodt_wheel_has_level_stack(self):
        _skip_if_no_artifacts()
        whl = ARTIFACTS_DIR / "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl"
        if not whl.exists():
            pytest.skip("FODT wheel not present")
        with zipfile.ZipFile(whl, "r") as zf:
            writer_names = [n for n in zf.namelist() if "writer.py" in n]
            src = zf.read(writer_names[0]).decode("utf-8")
        assert "level_stack" in src, "writer.py missing level_stack (R56 nested list)"


class TestPackageManifest:
    """Package manifest must exist with self_contained policy and full SHA-256 values."""

    def test_manifest_discovered(self):
        if MANIFEST_PATH is None:
            pytest.skip("Package manifest not available in this environment")
        assert MANIFEST_PATH.exists()

    def test_manifest_self_contained_policy(self):
        if MANIFEST_PATH is None:
            pytest.skip("Package manifest not available")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "self_contained" in content, "Manifest must declare self_contained policy"

    def test_manifest_sha256_values_are_64_chars(self):
        """All wheel_sha256 values in manifest must be 64 hex chars (R57 IV-R56-006 fix)."""
        if MANIFEST_PATH is None:
            pytest.skip("Package manifest not available")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        # Find all wheel_sha256 lines
        sha_lines = [line for line in content.splitlines() if "wheel_sha256" in line]
        if not sha_lines:
            pytest.skip("No wheel_sha256 lines found in manifest")
        for line in sha_lines:
            m = re.search(r'wheel_sha256[:\s]+([0-9a-fA-F]+)', line)
            if m:
                sha_val = m.group(1)
                assert len(sha_val) == 64, (
                    f"wheel_sha256 must be 64 chars (SHA-256), got {len(sha_val)} chars: {sha_val!r}. "
                    f"(IV-R56-006: R56 used MD5 values)"
                )
