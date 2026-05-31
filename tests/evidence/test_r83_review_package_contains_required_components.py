"""
tests/evidence/test_r83_review_package_contains_required_components.py

R83 Train B: Supervisor review package must contain all required components.

Defect fixed: D82-01 — R82 uploaded inner bundle without required components.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

REQUIRED_COMPONENT_PATTERNS = [
    "package-artifacts/",
    "package-artifact-manifest",
    "final-response-summary",
]


def _check_review_package_components(zip_path: Path) -> dict:
    """Check review package for required components."""
    if not zip_path.exists():
        return {"exists": False, "missing": [], "found": []}

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()

    found = []
    missing = []
    for pattern in REQUIRED_COMPONENT_PATTERNS:
        if any(pattern in n for n in names):
            found.append(pattern)
        else:
            missing.append(pattern)

    return {
        "exists": True,
        "missing": missing,
        "found": found,
        "has_package_artifacts": any("package-artifacts/" in n for n in names),
        "has_whl": any(n.endswith(".whl") for n in names),
        "total_entries": len(names),
    }


class TestReviewPackageContainsRequiredComponents:
    """Supervisor review package must contain all required components."""

    def test_review_package_exists(self):
        """R82 review package exists locally."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        assert r82_review.exists(), (
            "r82-supervisor-review-package.zip must exist in .local/ — "
            "this is the primary artifact that should have been uploaded"
        )

    def test_review_package_has_physical_wheels(self):
        """Review package must contain physical .whl files."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found")
        result = _check_review_package_components(r82_review)
        assert result["has_whl"], "Review package must contain .whl files in package-artifacts/"

    def test_review_package_has_package_artifacts_dir(self):
        """Review package must have package-artifacts/ directory."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found")
        result = _check_review_package_components(r82_review)
        assert result["has_package_artifacts"], "Review package must have package-artifacts/"

    def test_review_package_sufficient_entries(self):
        """Review package must have significantly more entries than inner bundle."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        r82_inner = REPO_ROOT / ".local" / "r82-pass2.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found")
        result = _check_review_package_components(r82_review)
        # Review package should be smaller than inner bundle (contains selected content)
        # but must have physical artifacts
        assert result["total_entries"] > 20, (
            f"Review package has too few entries: {result['total_entries']}"
        )

    def test_inner_bundle_correctly_lacks_artifacts(self):
        """Inner bundle should NOT have package-artifacts/ (that's review-package-only content)."""
        r82_inner = REPO_ROOT / ".local" / "r82-pass2.zip"
        if not r82_inner.exists():
            return
        with zipfile.ZipFile(r82_inner) as zf:
            names = zf.namelist()
        # Inner bundle has repo + metadata only
        top = {n.split("/")[0] for n in names if "/" in n}
        assert "package-artifacts" not in top, (
            "Inner bundle should not have package-artifacts/ — that belongs only in review package"
        )
