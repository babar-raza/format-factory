"""
test_r56_package_claim_consistency.py — R56 Train B: Package claim vs. policy consistency tests.

Validates the R56 rule: installed_artifact_policy: none cannot coexist with final verdict
language that claims packages were built, installed, or validated.

R56 Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
IV-R55-001, IV-R55-002
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_package_claim_policy_consistency


MANIFEST_NONE = "r55_installed_artifact_policy: none\nnote: No new packages built in R55.\n"
MANIFEST_SELF_CONTAINED = "installed_artifact_policy: self_contained\n"
CONTRACT_NONE = {"installed_artifact_policy": "none"}
CONTRACT_SELF_CONTAINED = {"installed_artifact_policy": "self_contained"}
CONTRACT_DEFAULT = {}  # defaults to none


class TestPackageClaimPolicyConsistency:

    def test_none_policy_with_no_package_language_passes(self):
        """Policy none + verdict with no package language is fine."""
        meta = {
            "final-verdict.md": "**Verdict:** R55_STATE_COMPLETE\nTests: 4411 passed\n",
            "package-artifact-manifest.yaml": MANIFEST_NONE,
        }
        errors = check_package_claim_policy_consistency(meta, CONTRACT_NONE)
        assert errors == [], f"No package claims should pass: {errors}"

    def test_none_policy_with_wheels_built_language_fails(self):
        """Policy none + verdict saying 'wheels built' is a contradiction (IV-R55-002)."""
        meta = {
            "final-verdict.md": "**Verdict:** R55_COMPLETE\nAll 7 packages built successfully. wheels built.\n",
            "package-artifact-manifest.yaml": MANIFEST_NONE,
        }
        errors = check_package_claim_policy_consistency(meta, CONTRACT_NONE)
        assert errors, "wheels built claim with policy none must fail"
        assert any("PACKAGE_CLAIM_POLICY_CONTRADICTION" in e for e in errors)

    def test_none_policy_with_installed_smoke_pass_fails(self):
        """Policy none + 'installed smoke pass' in verdict fails."""
        meta = {
            "final-verdict.md": "FODS/FODT installed smoke PASS from clean venv.\n",
            "package-artifact-manifest.yaml": MANIFEST_NONE,
        }
        errors = check_package_claim_policy_consistency(meta, CONTRACT_NONE)
        assert errors, "installed smoke PASS with policy none must fail"

    def test_self_contained_policy_with_wheel_language_passes(self):
        """Policy self_contained + package language is consistent."""
        meta = {
            "final-verdict.md": "7 packages built. wheels built. installed smoke PASS.\n",
            "package-artifact-manifest.yaml": MANIFEST_SELF_CONTAINED,
        }
        errors = check_package_claim_policy_consistency(meta, CONTRACT_SELF_CONTAINED)
        assert errors == [], f"self_contained with package language should pass: {errors}"

    def test_manifest_policy_overrides_contract_policy(self):
        """If manifest says 'none', the contract policy is overridden."""
        meta = {
            "final-verdict.md": "7 packages built.\n",
            "package-artifact-manifest.yaml": MANIFEST_NONE,  # manifest says none
        }
        # Even if contract says self_contained, manifest saying none triggers the check
        errors = check_package_claim_policy_consistency(meta, CONTRACT_SELF_CONTAINED)
        assert errors, "Manifest 'none' overrides contract; package claim must fail"

    def test_r55_defect_scenario_reproduced(self):
        """Reproduce R55 IV-R55-002: Phase Audit 6 claims 'All 7 packages BUILT' but manifest says none."""
        meta = {
            "final-verdict.md": (
                "| D | Package RC Self-Contained | COMPLETE | 7 packages built |\n"
                "Installed wheel smoke: PASS\n"
                "All 7 packages BUILT successfully.\n"
            ),
            "package-artifact-manifest.yaml": MANIFEST_NONE,
        }
        errors = check_package_claim_policy_consistency(meta, CONTRACT_DEFAULT)
        assert errors, "R55 IV-R55-002 defect scenario must fail validation"
        assert any("PACKAGE_CLAIM_POLICY_CONTRADICTION" in e for e in errors)

    def test_default_contract_with_package_rc_claim_fails(self):
        """Default contract (no installed_artifact_policy) with package RC claim fails."""
        meta = {
            "final-verdict.md": "Package RC complete. Installed wheel OK.\n",
            "package-artifact-manifest.yaml": MANIFEST_NONE,
        }
        errors = check_package_claim_policy_consistency(meta, CONTRACT_DEFAULT)
        assert errors, "default/none policy with package RC language must fail"

    def test_no_manifest_no_claim_passes(self):
        """No manifest + no package claim in verdict is fine."""
        meta = {
            "final-verdict.md": "Tests: 1000 passed.\n",
        }
        errors = check_package_claim_policy_consistency(meta, CONTRACT_DEFAULT)
        assert errors == [], f"No manifest, no claim should pass: {errors}"
