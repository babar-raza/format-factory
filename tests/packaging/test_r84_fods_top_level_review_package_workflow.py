"""
test_r84_fods_top_level_review_package_workflow.py

R84 Train F: Verify that the FODS package is accessible from the top-level
review package artifacts and that the installed API surface is correct.

Sprint: FORMAT-FACTORY-R84
"""
from __future__ import annotations

import zipfile
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_PACKAGE = PROJECT_ROOT / ".local" / "r84-supervisor-review-package.zip"
PACKAGE_ARTIFACTS = PROJECT_ROOT / ".local" / "r84-packages"


def _review_package_exists():
    return REVIEW_PACKAGE.exists()


def _package_artifacts_exist():
    return PACKAGE_ARTIFACTS.is_dir()


@pytest.mark.skipif(
    not _review_package_exists(),
    reason="R84 supervisor review package not yet built"
)
class TestFodsInReviewPackage:
    """Verify FODS wheel is accessible in top-level package-artifacts/ of review package."""

    def test_fods_wheel_in_package_artifacts_top_level(self):
        with zipfile.ZipFile(REVIEW_PACKAGE) as zf:
            names = zf.namelist()
        fods_wheels = [
            n for n in names
            if n.startswith("package-artifacts/") and "fods" in n and n.endswith(".whl")
        ]
        assert len(fods_wheels) >= 1, (
            "FODS wheel not found in top-level package-artifacts/ of review package"
        )

    def test_fodt_wheel_in_package_artifacts_top_level(self):
        with zipfile.ZipFile(REVIEW_PACKAGE) as zf:
            names = zf.namelist()
        fodt_wheels = [
            n for n in names
            if n.startswith("package-artifacts/") and "fodt" in n and n.endswith(".whl")
        ]
        assert len(fodt_wheels) >= 1, (
            "FODT wheel not found in top-level package-artifacts/ of review package"
        )


@pytest.mark.skipif(
    not _package_artifacts_exist(),
    reason="R84 package artifacts not yet built"
)
class TestFodsPackageArtifacts:
    """Verify FODS package artifacts are present in .local/r84-packages/."""

    def test_fods_wheel_exists_in_local_packages(self):
        wheels = list(PACKAGE_ARTIFACTS.rglob("*fods*.whl"))
        assert len(wheels) >= 1, "FODS wheel not found in .local/r84-packages/"

    def test_fodt_wheel_exists_in_local_packages(self):
        wheels = list(PACKAGE_ARTIFACTS.rglob("*fodt*.whl"))
        assert len(wheels) >= 1, "FODT wheel not found in .local/r84-packages/"

    def test_at_least_5_packages_present(self):
        wheels = list(PACKAGE_ARTIFACTS.rglob("*.whl"))
        assert len(wheels) >= 5, (
            f"Expected at least 5 wheels in package artifacts, found {len(wheels)}"
        )
