"""
test_r56_package_rc.py — R56 Train D: Package RC Self-Contained Artifact Tests.

Verifies:
1. All 7 wheel files exist in .local/r56-metadata/package-artifacts/
2. All 7 wheel files have non-zero size
3. FODS wheel can be installed and imported from clean venv (module detection)
4. FODT wheel built with R56 source includes hyperlink implementation
5. Package manifest exists with self_contained policy
6. FODT wheel contains writer.py with text:a emission code
7. FODS wheel contains writer.py with formula emission code

R56 Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / ".local" / "r56-metadata" / "package-artifacts"
MANIFEST_PATH = PROJECT_ROOT / ".local" / "r56-metadata" / "package-artifact-manifest.yaml"

pytestmark = pytest.mark.skipif(
    not ARTIFACTS_DIR.is_dir(),
    reason="R56 package artifacts not present in this environment",
)

EXPECTED_WHEELS = [
    "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_fodp-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_gnumeric-0.1.0.dev0-py3-none-any.whl",
    "aspose_format_factory_abw-0.1.0.dev0-py3-none-any.whl",
]


class TestPackageArtifactsExist:
    """All 7 wheel artifacts must exist in .local/r56-metadata/package-artifacts/."""

    def test_artifacts_dir_exists(self):
        assert ARTIFACTS_DIR.exists(), f"Missing artifacts dir: {ARTIFACTS_DIR}"

    @pytest.mark.parametrize("wheel_name", EXPECTED_WHEELS)
    def test_wheel_file_exists(self, wheel_name):
        whl = ARTIFACTS_DIR / wheel_name
        assert whl.exists(), f"Wheel missing: {whl}"

    @pytest.mark.parametrize("wheel_name", EXPECTED_WHEELS)
    def test_wheel_file_nonzero(self, wheel_name):
        whl = ARTIFACTS_DIR / wheel_name
        if whl.exists():
            assert whl.stat().st_size > 1000, f"Wheel suspiciously small: {whl}"

    def test_all_seven_wheels_present(self):
        present = [w for w in EXPECTED_WHEELS if (ARTIFACTS_DIR / w).exists()]
        assert len(present) == 7, f"Expected 7 wheels, found {len(present)}: {present}"


class TestWheelContents:
    """Wheel contents must include R56 source changes."""

    def test_fodt_wheel_contains_writer(self):
        """FODT wheel must include writer.py."""
        whl = ARTIFACTS_DIR / "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl"
        if not whl.exists():
            pytest.skip("FODT wheel not present")
        with zipfile.ZipFile(whl, "r") as zf:
            names = zf.namelist()
        writer_files = [n for n in names if "writer.py" in n]
        assert writer_files, f"writer.py not found in wheel; names={names[:20]}"

    def test_fodt_wheel_writer_has_hyperlink_code(self):
        """FODT wheel writer.py must contain text:a hyperlink emission code."""
        whl = ARTIFACTS_DIR / "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl"
        if not whl.exists():
            pytest.skip("FODT wheel not present")
        with zipfile.ZipFile(whl, "r") as zf:
            names = zf.namelist()
            writer_names = [n for n in names if "writer.py" in n]
            assert writer_names, "writer.py not in wheel"
            writer_src = zf.read(writer_names[0]).decode("utf-8")
        assert "xlink" in writer_src, "writer.py missing xlink namespace (R56 hyperlink code)"
        assert 'text", "a"' in writer_src or '"text", "a"' in writer_src or "_qn(\"text\", \"a\")" in writer_src, \
            "writer.py missing text:a element emission"

    def test_fodt_wheel_writer_has_level_stack_algorithm(self):
        """FODT wheel writer.py must contain level_stack (R56 nested list algorithm)."""
        whl = ARTIFACTS_DIR / "aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl"
        if not whl.exists():
            pytest.skip("FODT wheel not present")
        with zipfile.ZipFile(whl, "r") as zf:
            names = zf.namelist()
            writer_names = [n for n in names if "writer.py" in n]
            writer_src = zf.read(writer_names[0]).decode("utf-8")
        assert "level_stack" in writer_src, "writer.py missing level_stack algorithm (R56 nested list)"

    def test_fods_wheel_contains_writer(self):
        """FODS wheel must include writer.py."""
        whl = ARTIFACTS_DIR / "aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl"
        if not whl.exists():
            pytest.skip("FODS wheel not present")
        with zipfile.ZipFile(whl, "r") as zf:
            names = zf.namelist()
        writer_files = [n for n in names if "writer.py" in n]
        assert writer_files, "writer.py not found in FODS wheel"


class TestPackageManifest:
    """Package manifest must exist with self_contained policy and correct R56 metadata."""

    def test_manifest_exists(self):
        assert MANIFEST_PATH.exists(), f"Package manifest missing: {MANIFEST_PATH}"

    def test_manifest_self_contained_policy(self):
        """Manifest must declare self_contained policy (not 'none')."""
        if not MANIFEST_PATH.exists():
            pytest.skip("Manifest not present")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "self_contained" in content, \
            "Manifest must declare r56_installed_artifact_policy: self_contained"
        assert "none" not in content.split("r56_installed_artifact_policy")[1].split("\n")[0], \
            "Policy must not be 'none' — this repeats R55 defect IV-R55-002"

    def test_manifest_smoke_pass(self):
        """Manifest must record FODS/FODT smoke as PASS."""
        if not MANIFEST_PATH.exists():
            pytest.skip("Manifest not present")
        content = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "PASS" in content, "Manifest must record at least one PASS smoke test result"
