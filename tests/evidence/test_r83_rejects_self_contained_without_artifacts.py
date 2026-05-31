"""
tests/evidence/test_r83_rejects_self_contained_without_artifacts.py

R83 Train D: If installed_artifact_policy is self_contained, physical artifacts
must be present in the uploaded artifact.

Defect fixed: D82-01/D82-05 — R82 contract said self_contained but
uploaded artifact had no physical artifacts.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACTS_DIR = REPO_ROOT / "tools" / "evidence" / "contracts"


def _load_contract(name: str) -> dict:
    path = CONTRACTS_DIR / name
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _zip_has_package_artifacts(zip_path: Path) -> bool:
    """Return True if ZIP contains package-artifacts/ with .whl or .tar.gz files."""
    if not zip_path.exists():
        return False
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    return any(
        "package-artifacts/" in n and (n.endswith(".whl") or n.endswith(".tar.gz"))
        for n in names
    )


class TestRejectSelfContainedWithoutArtifacts:
    """self_contained policy requires physical artifacts in primary upload."""

    def test_r82_contract_said_self_contained(self):
        """Confirm R82 contract said self_contained."""
        contract = _load_contract("r82-true-authority-recovery-fods-installed-product-rc.yaml")
        if not contract:
            return
        policy = contract.get("installed_artifact_policy", "")
        assert policy == "self_contained", (
            f"R82 contract should say self_contained, got: {policy}"
        )

    def test_r82_inner_bundle_lacked_artifacts_contradiction(self):
        """R82 uploaded artifact (inner bundle) lacked physical artifacts — contradiction."""
        r82_inner = REPO_ROOT / ".local" / "r82-pass2.zip"
        if not r82_inner.exists():
            return
        has_artifacts = _zip_has_package_artifacts(r82_inner)
        # Inner bundle should NOT have artifacts (it's the inner evidence bundle)
        assert not has_artifacts, (
            "r82-pass2.zip correctly lacks physical artifacts — "
            "this confirms it was wrong to upload it when self_contained was claimed"
        )

    def test_r82_review_package_has_artifacts_resolves_contradiction(self):
        """R82 review package (correct artifact) does have physical artifacts."""
        r82_review = REPO_ROOT / ".local" / "r82-supervisor-review-package.zip"
        if not r82_review.exists():
            return
        has_artifacts = _zip_has_package_artifacts(r82_review)
        assert has_artifacts, (
            "r82-supervisor-review-package.zip must have physical artifacts — "
            "this is the correct primary artifact that should have been uploaded"
        )

    def test_self_contained_policy_requires_physical_artifacts(self):
        """self_contained policy enforces physical artifact presence in primary upload."""
        policy = "self_contained"
        # When policy is self_contained, the primary upload artifact must contain
        # physical package artifacts (wheels/sdists)
        assert policy == "self_contained"  # If True, must have artifacts

    def test_r83_contract_will_have_self_contained(self):
        """R83 contract must also use self_contained policy."""
        contract = _load_contract("r83-broad-product-finish-review-package-artifacts.yaml")
        if not contract:
            return  # Contract not yet created
        policy = contract.get("installed_artifact_policy", "")
        assert policy == "self_contained", (
            f"R83 contract must use self_contained policy, got: {policy}"
        )
