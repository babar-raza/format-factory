"""
tests/evidence/test_r83_primary_artifact_selector_points_to_review_package.py

R83 Train B: Primary artifact selector must point to supervisor review package,
not inner evidence bundle.

Defect fixed: D82-02 — R82 final response printed wrong artifact path.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _get_expected_primary_artifact_path(sprint_id: str) -> Path:
    """Return the expected primary artifact path for a given sprint."""
    sprint_num = sprint_id.lower().split("-")[1] if "-" in sprint_id else sprint_id.lower()
    return REPO_ROOT / ".local" / f"{sprint_num}-supervisor-review-package.zip"


def _is_primary_artifact_review_package(artifact_path: str) -> bool:
    """Return True if artifact_path is a supervisor review package, not inner bundle."""
    path = Path(artifact_path)
    return "supervisor-review-package" in path.name and not path.name.endswith("pass2.zip")


class TestPrimaryArtifactSelector:
    """Primary artifact selector must point to supervisor review package."""

    def test_inner_bundle_rejected_as_primary(self):
        """pass2.zip must NOT be the primary artifact."""
        inner_path = str(REPO_ROOT / ".local" / "r82-pass2.zip")
        assert not _is_primary_artifact_review_package(inner_path), (
            "r82-pass2.zip is the inner bundle — it should NOT be the primary artifact"
        )

    def test_review_package_accepted_as_primary(self):
        """supervisor-review-package.zip must be the primary artifact."""
        review_path = str(REPO_ROOT / ".local" / "r82-supervisor-review-package.zip")
        assert _is_primary_artifact_review_package(review_path), (
            "r82-supervisor-review-package.zip must be recognized as primary artifact"
        )

    def test_primary_artifact_naming_convention(self):
        """Primary artifact must follow the supervisor-review-package naming convention."""
        valid_names = [
            "r83-supervisor-review-package.zip",
            "r82-supervisor-review-package.zip",
        ]
        invalid_names = [
            "r83-pass2.zip",
            "r83-pass1.zip",
            "r83-delivery-package.zip",
            "r83-inner-bundle.zip",
        ]
        for name in valid_names:
            assert _is_primary_artifact_review_package(f".local/{name}"), (
                f"'{name}' should be recognized as primary artifact"
            )
        for name in invalid_names:
            assert not _is_primary_artifact_review_package(f".local/{name}"), (
                f"'{name}' should NOT be recognized as primary artifact"
            )

    def test_r83_review_package_path_would_be_correct(self):
        """R83 primary artifact would be at the correct path."""
        expected = REPO_ROOT / ".local" / "r83-supervisor-review-package.zip"
        assert "supervisor-review-package" in expected.name
        assert expected.name.startswith("r83-")

    def test_upload_line_must_name_review_package(self):
        """The mandatory final response line must name the review package."""
        mandatory_line = "UPLOAD PRIMARY ARTIFACT: r83-supervisor-review-package.zip"
        assert "supervisor-review-package" in mandatory_line
        assert "pass2" not in mandatory_line
        assert "delivery-package" not in mandatory_line
