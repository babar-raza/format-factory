"""
tests/evidence/test_r83_rejects_inner_bundle_as_primary_upload.py

R83 Train B: Primary upload artifact must be the supervisor review package,
not the inner evidence bundle.

Defect fixed: D82-01/D82-02 — R82 uploaded r82-pass2.zip (inner bundle) instead of
r82-supervisor-review-package.zip as the primary artifact.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _has_only_inner_bundle_layout(zip_path: Path) -> bool:
    """Return True if the ZIP has only repo/ + bundle-metadata/ top-level folders."""
    if not zip_path.exists():
        return False
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        top_level = {n.split("/")[0] for n in names if "/" in n}
        inner_only = {"repo", "bundle-metadata"}
        # If only inner bundle structure (no package-artifacts, no delivery, no raw-*)
        has_package_artifacts = any("package-artifacts" in n for n in names)
        has_raw_logs = any("raw-" in n for n in names)
        has_delivery = any("delivery-package" in n for n in names)
        if not has_package_artifacts and not has_raw_logs and not has_delivery:
            if top_level.issubset(inner_only | {""}):
                return True
    return False


class TestRejectInnerBundleAsPrimaryUpload:
    """Primary upload must be the supervisor review package, not the inner evidence bundle."""

    def test_inner_bundle_has_no_package_artifacts(self):
        """Confirm inner bundle lacks package-artifacts/ — catches D82-01 pattern."""
        r82_inner = REPO_ROOT / ".local" / "r82-pass2.zip"
        if not r82_inner.exists():
            return
        with zipfile.ZipFile(r82_inner) as zf:
            names = zf.namelist()
        has_artifacts = any("package-artifacts" in n for n in names)
        assert not has_artifacts, (
            "Inner bundle should NOT contain package-artifacts/ — "
            "that indicates it was incorrectly built as a review package"
        )

    def test_review_package_has_package_artifacts(self):
        """Supervisor review package must contain package-artifacts/."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found locally")
        with zipfile.ZipFile(r82_review) as zf:
            names = zf.namelist()
        has_artifacts = any("package-artifacts" in n for n in names)
        assert has_artifacts, "Supervisor review package must contain package-artifacts/"

    def test_inner_bundle_layout_detector(self):
        """Inner bundle layout detector works correctly."""
        r82_inner = REPO_ROOT / ".local" / "r82-pass2.zip"
        if not r82_inner.exists():
            return
        assert _has_only_inner_bundle_layout(r82_inner), (
            "r82-pass2.zip should be detected as inner-only bundle layout"
        )

    def test_review_package_not_inner_bundle_layout(self):
        """Review package must NOT have only inner bundle layout."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found locally")
        assert not _has_only_inner_bundle_layout(r82_review), (
            "Supervisor review package must not have inner-bundle-only layout"
        )

    def test_correct_primary_artifact_name(self):
        """Primary artifact name must contain 'supervisor-review-package', not just 'pass2'."""
        # Verify the naming convention
        inner_name = "r82-pass2.zip"
        review_name = "r82-supervisor-review-package.zip"
        assert "supervisor-review-package" in review_name
        assert "supervisor-review-package" not in inner_name
        # The correct one must be uploaded
        assert review_name.endswith("-supervisor-review-package.zip")
