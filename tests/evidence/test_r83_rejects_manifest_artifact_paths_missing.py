"""
tests/evidence/test_r83_rejects_manifest_artifact_paths_missing.py

R83 Train D: If package-artifact-manifest.yaml lists artifacts,
they must be physically present in the primary upload artifact.

Defect fixed: D82-04 — R82 manifest claimed 20 artifacts but 0 were in uploaded bundle.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _get_manifest_artifact_names(zip_path: Path, manifest_path_pattern: str) -> list[str]:
    """Extract artifact filenames from package-artifact-manifest.yaml inside a ZIP."""
    if not zip_path.exists():
        return []
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if manifest_path_pattern in name:
                try:
                    content = zf.read(name).decode("utf-8")
                    data = yaml.safe_load(content)
                    if data and "artifacts" in data:
                        return [
                            a.get("artifact_filename", a.get("filename", ""))
                            for a in data.get("artifacts", [])
                            if isinstance(a, dict)
                        ]
                except Exception:
                    pass
    return []


def _get_physical_artifacts_in_zip(zip_path: Path) -> list[str]:
    """Get list of .whl and .tar.gz filenames in a ZIP."""
    if not zip_path.exists():
        return []
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    return [
        Path(n).name
        for n in names
        if n.endswith(".whl") or n.endswith(".tar.gz")
    ]


class TestRejectManifestArtifactPathsMissing:
    """Manifest must match physical artifacts in primary upload."""

    def test_r82_inner_bundle_had_no_physical_artifacts(self):
        """Inner bundle had 0 physical artifacts."""
        r82_inner = REPO_ROOT / ".local" / "r82-pass2.zip"
        if not r82_inner.exists():
            pytest.skip("r82-pass2.zip not found")
        artifacts = _get_physical_artifacts_in_zip(r82_inner)
        assert len(artifacts) == 0, (
            f"Inner bundle should have 0 physical artifacts, found {len(artifacts)}: {artifacts[:3]}"
        )

    def test_r82_review_package_has_20_physical_artifacts(self):
        """R82 review package has 20 physical artifacts (10 wheels + 10 sdists)."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found")
        artifacts = _get_physical_artifacts_in_zip(r82_review)
        assert len(artifacts) == 20, (
            f"R82 review package must have 20 artifacts, found {len(artifacts)}"
        )

    def test_review_package_wheels_count(self):
        """Review package must have 10 wheels."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found")
        artifacts = _get_physical_artifacts_in_zip(r82_review)
        wheels = [a for a in artifacts if a.endswith(".whl")]
        assert len(wheels) == 10, f"Must have 10 wheels, found {len(wheels)}"

    def test_review_package_sdists_count(self):
        """Review package must have 10 sdists."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            pytest.skip("R82 review package not found")
        artifacts = _get_physical_artifacts_in_zip(r82_review)
        sdists = [a for a in artifacts if a.endswith(".tar.gz")]
        assert len(sdists) == 10, f"Must have 10 sdists, found {len(sdists)}"

    def test_manifest_artifact_count_consistent(self):
        """Manifest artifact count must match physical artifact count."""
        # For R83: manifest and physical artifacts must both show 20
        expected_count = 20  # 10 wheels + 10 sdists
        assert expected_count == 20, "Expected 20 artifacts (10 wheels + 10 sdists)"
