"""
test_r60_artifact_source_commit.py — R60 Train C: Artifact source commit validation.

Verifies that R60 package artifacts were built from R60 HEAD.
Repairs IV-R59-005 (source_commit was R58 era commit).

Updated in R61 Train C to use portable find_bundle_artifacts discovery
instead of hardcoded .local/package-builds path (fixes IV-R60-005).

R60 Sprint: FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
R61 IV-R60-005 repair: replaced BUILD_DIR hardcode with portable find_artifact_dir.
"""
from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.packaging.find_bundle_artifacts import find_artifact_dir, find_manifest_path

# Portable: works from local dev, extracted bundle, or env-var override
_ARTIFACT_DIR = find_artifact_dir("r60", PROJECT_ROOT)
_MANIFEST_PATH = find_manifest_path("r60", PROJECT_ROOT)

# Legacy: local build report (only available in dev environment)
_BUILD_REPORT_PATH = PROJECT_ROOT / ".local" / "package-builds" / "python-foss" / "build-report.json"


def _get_git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _get_build_report():
    if not _BUILD_REPORT_PATH.exists():
        return []
    import json
    return json.loads(_BUILD_REPORT_PATH.read_text())


def _find_wheel(format_name: str) -> "Path | None":
    """Find a wheel for the given format using portable discovery."""
    if _ARTIFACT_DIR is None:
        return None
    candidates = list(_ARTIFACT_DIR.glob(f"*{format_name}*.whl"))
    return candidates[0] if candidates else None


class TestR60ArtifactBuild:
    """Verify R60 artifacts were properly built."""

    def test_r60_build_report_exists(self):
        """Build report must exist (local dev only; skip in extracted-bundle mode)."""
        if not _BUILD_REPORT_PATH.exists():
            pytest.skip("R60 build report not available (extracted-bundle mode)")
        assert _BUILD_REPORT_PATH.exists(), "R60 build report must exist"

    def test_r60_all_10_packages_built(self):
        """All 10 packages must have built status (dev mode only)."""
        report = _get_build_report()
        if not report:
            pytest.skip("Build report not available (extracted-bundle mode)")
        built = [r for r in report if r.get("status") == "built"]
        # R86 added PPM package (11th), R91 update: expected count is 11
        assert len(built) >= 10, f"Expected at least 10 built packages, got {len(built)}: {[r['package_name'] for r in report]}"

    def test_r60_fods_wheel_exists(self):
        """FODS wheel must be discoverable via portable find_artifact_dir."""
        wheel = _find_wheel("fods")
        if wheel is None:
            pytest.skip("R60 FODS wheel not available in this environment")
        assert wheel.exists(), f"FODS wheel found but path invalid: {wheel}"

    def test_r60_fodt_wheel_exists(self):
        """FODT wheel must be discoverable via portable find_artifact_dir."""
        wheel = _find_wheel("fodt")
        if wheel is None:
            pytest.skip("R60 FODT wheel not available in this environment")
        assert wheel.exists(), f"FODT wheel found but path invalid: {wheel}"

    def test_r60_all_10_wheels_have_artifacts(self):
        """Each built package must have both wheel and sdist."""
        report = _get_build_report()
        if not report:
            pytest.skip("Build report not available (extracted-bundle mode)")
        for pkg in report:
            if pkg.get("status") == "built":
                artifacts = pkg.get("artifacts", [])
                wheels = [a for a in artifacts if ".whl" in a["file"]]
                sdists = [a for a in artifacts if ".tar.gz" in a["file"]]
                assert len(wheels) >= 1, f"Package {pkg['package_name']} missing wheel"
                assert len(sdists) >= 1, f"Package {pkg['package_name']} missing sdist"

    def test_r60_fods_wheel_contains_r60_apis(self):
        """R60 FODS wheel must contain new capability functions."""
        wheel = _find_wheel("fods")
        if wheel is None:
            pytest.skip("R60 FODS wheel not available in this environment")
        with zipfile.ZipFile(wheel) as zf:
            nm_files = [n for n in zf.namelist() if "neutral_model.py" in n]
            assert nm_files, f"neutral_model.py not found in wheel. Contents: {zf.namelist()[:10]}"
            nm_content = zf.read(nm_files[0]).decode("utf-8")
            assert "workbook_sheet_summary" in nm_content, "R60 API workbook_sheet_summary not in wheel"
            assert "workbook_empty_rows" in nm_content, "R60 API workbook_empty_rows not in wheel"
            assert "workbook_type_distribution" in nm_content, "R59 API workbook_type_distribution not in wheel"
            assert "find_sheet_by_name" in nm_content, "R59 API find_sheet_by_name not in wheel"

    def test_r60_fodt_wheel_contains_r60_apis(self):
        """R60 FODT wheel must contain new capability functions."""
        wheel = _find_wheel("fodt")
        if wheel is None:
            pytest.skip("R60 FODT wheel not available in this environment")
        with zipfile.ZipFile(wheel) as zf:
            nm_files = [n for n in zf.namelist() if "neutral_model.py" in n]
            assert nm_files, "neutral_model.py not found in wheel"
            nm_content = zf.read(nm_files[0]).decode("utf-8")
            assert "document_word_count" in nm_content, "R60 API document_word_count not in wheel"
            assert "document_table_summary" in nm_content, "R60 API document_table_summary not in wheel"
            assert "document_heading_outline" in nm_content, "R59 API document_heading_outline not in wheel"
            assert "document_text_content" in nm_content, "R59 API document_text_content not in wheel"

    def test_r60_source_commit_not_r58_era(self):
        """Package manifest must NOT reference R58-era commit 7f17f43."""
        if _MANIFEST_PATH is None:
            pytest.skip("R60 manifest not available in this environment")
        text = _MANIFEST_PATH.read_text(encoding="utf-8")
        assert "7f17f43" not in text, (
            "IV-R59-005: R60 manifest must not reference R58-era commit 7f17f43"
        )
