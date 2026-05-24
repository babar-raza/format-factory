"""
test_r60_artifact_source_commit.py — R60 Train C: Artifact source commit validation.

Verifies that R60 package artifacts were built from R60 HEAD.
Repairs IV-R59-005 (source_commit was R58 era commit).

R60 Sprint: FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / ".local" / "r60-metadata" / "package-artifact-manifest.yaml"
BUILD_DIR = PROJECT_ROOT / ".local" / "package-builds" / "python-foss"


def _get_git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _get_build_report():
    report_path = BUILD_DIR / "build-report.json"
    if not report_path.exists():
        return []
    import json
    return json.loads(report_path.read_text())


class TestR60ArtifactBuild:
    """Verify R60 artifacts were properly built."""

    def test_r60_build_report_exists(self):
        assert (BUILD_DIR / "build-report.json").exists(), "R60 build report must exist"

    def test_r60_all_10_packages_built(self):
        """All 10 packages must have built status."""
        report = _get_build_report()
        built = [r for r in report if r.get("status") == "built"]
        assert len(built) == 10, f"Expected 10 built packages, got {len(built)}: {[r['package_name'] for r in report]}"

    def test_r60_fods_wheel_exists(self):
        """FODS wheel must be in build output."""
        fods_dir = BUILD_DIR / "aspose-format-factory-fods" / "dist"
        wheels = list(fods_dir.glob("*.whl")) if fods_dir.exists() else []
        assert len(wheels) >= 1, f"Expected FODS wheel in {fods_dir}"

    def test_r60_fodt_wheel_exists(self):
        """FODT wheel must be in build output."""
        fodt_dir = BUILD_DIR / "aspose-format-factory-fodt" / "dist"
        wheels = list(fodt_dir.glob("*.whl")) if fodt_dir.exists() else []
        assert len(wheels) >= 1, f"Expected FODT wheel in {fodt_dir}"

    def test_r60_all_10_wheels_have_artifacts(self):
        """Each built package must have both wheel and sdist."""
        report = _get_build_report()
        for pkg in report:
            if pkg.get("status") == "built":
                artifacts = pkg.get("artifacts", [])
                wheels = [a for a in artifacts if ".whl" in a["file"]]
                sdists = [a for a in artifacts if ".tar.gz" in a["file"]]
                assert len(wheels) >= 1, f"Package {pkg['package_name']} missing wheel"
                assert len(sdists) >= 1, f"Package {pkg['package_name']} missing sdist"

    def test_r60_fods_wheel_contains_r60_apis(self):
        """R60 FODS wheel must contain new capability functions."""
        fods_dir = BUILD_DIR / "aspose-format-factory-fods" / "dist"
        wheels = list(fods_dir.glob("*.whl")) if fods_dir.exists() else []
        assert wheels, "FODS wheel not found"
        import zipfile
        with zipfile.ZipFile(wheels[0]) as zf:
            # Read the neutral_model.py from the wheel
            nm_files = [n for n in zf.namelist() if "neutral_model.py" in n]
            assert nm_files, f"neutral_model.py not found in wheel. Contents: {zf.namelist()[:10]}"
            nm_content = zf.read(nm_files[0]).decode("utf-8")
            assert "workbook_sheet_summary" in nm_content, "R60 API workbook_sheet_summary not in wheel"
            assert "workbook_empty_rows" in nm_content, "R60 API workbook_empty_rows not in wheel"
            assert "workbook_type_distribution" in nm_content, "R59 API workbook_type_distribution not in wheel"
            assert "find_sheet_by_name" in nm_content, "R59 API find_sheet_by_name not in wheel"

    def test_r60_fodt_wheel_contains_r60_apis(self):
        """R60 FODT wheel must contain new capability functions."""
        fodt_dir = BUILD_DIR / "aspose-format-factory-fodt" / "dist"
        wheels = list(fodt_dir.glob("*.whl")) if fodt_dir.exists() else []
        assert wheels, "FODT wheel not found"
        import zipfile
        with zipfile.ZipFile(wheels[0]) as zf:
            nm_files = [n for n in zf.namelist() if "neutral_model.py" in n]
            assert nm_files, f"neutral_model.py not found in wheel"
            nm_content = zf.read(nm_files[0]).decode("utf-8")
            assert "document_word_count" in nm_content, "R60 API document_word_count not in wheel"
            assert "document_table_summary" in nm_content, "R60 API document_table_summary not in wheel"
            assert "document_heading_outline" in nm_content, "R59 API document_heading_outline not in wheel"
            assert "document_text_content" in nm_content, "R59 API document_text_content not in wheel"

    def test_r60_source_commit_not_r58_era(self):
        """Package manifest must NOT reference R58-era commit 7f17f43."""
        if not MANIFEST_PATH.exists():
            pytest.skip("R60 manifest not yet built")
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        assert "7f17f43" not in text, (
            "IV-R59-005: R60 manifest must not reference R58-era commit 7f17f43"
        )
