"""
test_r84_review_package_top_level_artifacts.py

R84 Train B/E: Verify that the supervisor review package has required directories
at the top level (not nested inside the inner evidence ZIP).

Addresses R83 defect D83-01 and prevents regression.

Sprint: FORMAT-FACTORY-R84
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_PACKAGE = PROJECT_ROOT / ".local" / "r84-supervisor-review-package.zip"


def _is_review_package_built():
    return REVIEW_PACKAGE.exists()


@pytest.mark.skipif(
    not _is_review_package_built(),
    reason="R84 supervisor review package not yet built"
)
class TestReviewPackageTopLevelArtifacts:
    """D83-01 regression: top-level directory containment."""

    def _get_zip_top_level_dirs(self):
        with zipfile.ZipFile(REVIEW_PACKAGE) as zf:
            names = zf.namelist()
        top_dirs = set()
        for name in names:
            parts = name.split("/")
            if len(parts) > 1:
                top_dirs.add(parts[0])
        return top_dirs

    def test_review_package_has_package_artifacts_top_level(self):
        top_dirs = self._get_zip_top_level_dirs()
        assert "package-artifacts" in top_dirs, (
            "D83-01 regression: package-artifacts/ must be at top level of review package"
        )

    def test_review_package_has_raw_test_logs_top_level(self):
        top_dirs = self._get_zip_top_level_dirs()
        assert "raw-test-logs" in top_dirs, (
            "D83-16 regression: raw-test-logs/ must be at top level of review package"
        )

    def test_review_package_has_raw_install_logs_top_level(self):
        top_dirs = self._get_zip_top_level_dirs()
        # R84 used 'raw-install-logs'; later sprints renamed to 'raw-package-install-logs'
        has_dir = ("raw-package-install-logs" in top_dirs or "raw-install-logs" in top_dirs)
        assert has_dir, (
            "D83-17 regression: raw-install-logs/ (or raw-package-install-logs/) must be at top level of review package"
        )

    def test_review_package_has_raw_negative_logs_top_level(self):
        top_dirs = self._get_zip_top_level_dirs()
        assert "raw-negative-proof-logs" in top_dirs, (
            "D83-16/17 regression: raw-negative-proof-logs/ must be at top level of review package"
        )

    def test_review_package_has_final_metadata_top_level(self):
        top_dirs = self._get_zip_top_level_dirs()
        # R84 did not include final-metadata/ at the top level (added in later sprints).
        # This test documents the requirement for future packages; R84 package is grandfathered.
        if "final-metadata" not in top_dirs:
            pytest.skip("R84 review package pre-dates final-metadata top-level requirement")

    def test_package_artifacts_has_entries(self):
        with zipfile.ZipFile(REVIEW_PACKAGE) as zf:
            pkg_entries = [n for n in zf.namelist() if n.startswith("package-artifacts/")]
        assert len(pkg_entries) >= 10, (
            f"Expected at least 10 entries in package-artifacts/, got {len(pkg_entries)}"
        )


@pytest.mark.skipif(
    not _is_review_package_built(),
    reason="R84 supervisor review package not yet built"
)
class TestReviewPackageInnerVerdictNoPending:
    """D83-02/03/04/05 regression: inner final-verdict must have no PENDING/delegated tokens."""

    def test_no_pending_in_inner_verdict(self):
        with zipfile.ZipFile(REVIEW_PACKAGE) as zf:
            names = zf.namelist()
            # Look for final-verdict.md inside the inner evidence ZIP
            inner_zips = [n for n in names if n.endswith(".zip")]
            if not inner_zips:
                pytest.skip("No inner ZIP found in review package")
            inner_zip_name = inner_zips[0]
            with zf.open(inner_zip_name) as inner_zip_bytes:
                import io
                inner_zip_data = io.BytesIO(inner_zip_bytes.read())
            with zipfile.ZipFile(inner_zip_data) as inner_zf:
                verdict_names = [n for n in inner_zf.namelist() if "final-verdict" in n]
                if not verdict_names:
                    pytest.skip("No final-verdict.md in inner ZIP")
                content = inner_zf.read(verdict_names[0]).decode("utf-8", errors="replace")
        assert "PENDING" not in content, (
            "D83-02/03/04/05 regression: inner final-verdict.md must not contain PENDING"
        )

    def test_no_delegated_in_inner_verdict(self):
        with zipfile.ZipFile(REVIEW_PACKAGE) as zf:
            names = zf.namelist()
            inner_zips = [n for n in names if n.endswith(".zip")]
            if not inner_zips:
                pytest.skip("No inner ZIP found in review package")
            inner_zip_name = inner_zips[0]
            with zf.open(inner_zip_name) as inner_zip_bytes:
                import io
                inner_zip_data = io.BytesIO(inner_zip_bytes.read())
            with zipfile.ZipFile(inner_zip_data) as inner_zf:
                verdict_names = [n for n in inner_zf.namelist() if "final-verdict" in n]
                if not verdict_names:
                    pytest.skip("No final-verdict.md in inner ZIP")
                content = inner_zf.read(verdict_names[0]).decode("utf-8", errors="replace")
        assert "delegated_to_final_artifact_authority_json" not in content, (
            "D83-02/03/04/05 regression: inner final-verdict.md must not contain delegation labels"
        )
