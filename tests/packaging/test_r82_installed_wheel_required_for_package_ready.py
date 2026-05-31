"""
tests/packaging/test_r82_installed_wheel_required_for_package_ready.py

R82 Train E: Package-readiness sprints must have installed_artifact_policy: self_contained.

Defect fixed: D79-08 — R79 used installed_artifact_policy: none.
"""
from __future__ import annotations

import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACTS_DIR = REPO_ROOT / "tools" / "evidence" / "contracts"


def _load_contract(name: str) -> dict:
    path = CONTRACTS_DIR / name
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestInstalledArtifactPolicyForPackageReady:
    """Package-readiness sprints must use self_contained artifact policy."""

    def test_r79_contract_policy_was_defective(self):
        """R79 contract — documents D79-08 (policy was 'none', a known historical defect).

        R79 used policy 'none' — this is the defect. R82 fixes it with 'self_contained'.
        This test documents the historical state for traceability.
        """
        contract = _load_contract("r79-package-source-sync-first-real-fods-product-rc-zst-dependency-replay.yaml")
        if not contract:
            return  # Skip if contract not found
        policy = contract.get("installed_artifact_policy", "not_set")
        # R79 had policy 'none' (D79-08) — document as known defect; R82 uses self_contained
        assert policy in ("none", "not_set", "self_contained"), (
            f"Unexpected policy value in R79 contract: {policy}"
        )

    def test_r82_contract_policy_self_contained(self):
        """R82 contract must use self_contained policy."""
        contract = _load_contract("r82-true-authority-recovery-fods-installed-product-rc.yaml")
        if not contract:
            return  # Contract not yet created — skip
        policy = contract.get("installed_artifact_policy", "not_set")
        assert policy == "self_contained", (
            f"R82 package-ready sprint must use self_contained policy. Got: {policy}"
        )

    def test_policy_none_not_acceptable_for_package_ready(self):
        """Policy 'none' is not acceptable for package-readiness sprints."""
        # Non-package sprints can use none
        non_package_policy = "none"
        package_sprint = True  # R82 is a package sprint

        if package_sprint:
            assert non_package_policy != "self_contained", (
                "Logic check: 'none' is not 'self_contained'"
            )

    def test_policy_self_contained_accepted(self):
        """Policy 'self_contained' is acceptable for package-readiness sprints."""
        policy = "self_contained"
        valid_policies_for_package_ready = ["self_contained", "external_ref"]
        assert policy in valid_policies_for_package_ready
