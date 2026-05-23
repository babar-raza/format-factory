"""
test_r54_artifact_policy.py — R54 Lane 3 tests for installed_artifact_policy enforcement.

Tests:
  - self_contained: missing artifacts fails
  - external_ref: missing prior SHA fails
  - none + clean-baseline verdict fails
  - partial/product-validator sprint with no artifact claim passes

R54 Sprint: FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import check_installed_artifact_policy


def _make_zf(entries: dict[str, str]) -> zipfile.ZipFile:
    """Build an in-memory ZipFile from a dict of {path: content}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


class TestArtifactPolicyNone:
    """installed_artifact_policy: none (default)."""

    def test_default_no_policy_and_partial_verdict_passes(self):
        contract = {}
        meta = {}
        with _make_zf({"repo/state/current-state.md": ""}) as zf:
            errors = check_installed_artifact_policy(
                contract, meta, zf,
                verdict_content="R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL"
            )
        assert errors == []

    def test_none_policy_with_installed_baseline_verdict_fails(self):
        contract = {"installed_artifact_policy": "none"}
        meta = {}
        with _make_zf({}) as zf:
            errors = check_installed_artifact_policy(
                contract, meta, zf,
                verdict_content="R52_INSTALLED_ARTIFACT_BASELINE_CLEAN"
            )
        assert len(errors) == 1
        assert "ARTIFACT_POLICY_VIOLATION" in errors[0]

    def test_none_policy_with_no_baseline_verdict_passes(self):
        contract = {"installed_artifact_policy": "none"}
        meta = {}
        with _make_zf({}) as zf:
            errors = check_installed_artifact_policy(
                contract, meta, zf,
                verdict_content="R54_SIDECAR_FAIL_CLOSED_FODT_PRESERVATION_ADVANCED_PHASE5_PARTIAL"
            )
        assert errors == []


class TestArtifactPolicySelfContained:
    """installed_artifact_policy: self_contained."""

    def test_self_contained_with_wheel_passes(self):
        contract = {"installed_artifact_policy": "self_contained"}
        meta = {}
        with _make_zf({
            "bundle-metadata/package-artifacts/format_factory_fods-0.1.0-py3-none-any.whl": "wheel"
        }) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert errors == []

    def test_self_contained_no_artifacts_fails(self):
        contract = {"installed_artifact_policy": "self_contained"}
        meta = {}
        with _make_zf({"repo/state/current-state.md": "state"}) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert len(errors) == 1
        assert "ARTIFACT_POLICY_SELF_CONTAINED" in errors[0]

    def test_self_contained_with_sdist_passes(self):
        contract = {"installed_artifact_policy": "self_contained"}
        meta = {}
        with _make_zf({
            "bundle-metadata/package-artifacts/format_factory_fods-0.1.0.tar.gz": "sdist"
        }) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert errors == []

    def test_self_contained_with_nupkg_passes(self):
        contract = {"installed_artifact_policy": "self_contained"}
        meta = {}
        with _make_zf({
            "bundle-metadata/package-artifacts/FormatFactory.Fods.1.0.0.nupkg": "pkg"
        }) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert errors == []


class TestArtifactPolicyExternalRef:
    """installed_artifact_policy: external_ref."""

    def test_external_ref_with_complete_manifest_passes(self):
        contract = {"installed_artifact_policy": "external_ref"}
        meta = {
            "package-artifact-manifest.yaml": (
                "prior_bundle_filename: r51-installed-artifact-baseline.zip\n"
                "prior_bundle_sha256: abc123def456abc123def456abc123def456abc123def456abc123def456abc1\n"
                "verification: artifacts are in R51 bundle, verified by state validator\n"
            )
        }
        with _make_zf({}) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert errors == []

    def test_external_ref_missing_manifest_fails(self):
        contract = {"installed_artifact_policy": "external_ref"}
        meta = {}
        with _make_zf({}) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert len(errors) == 1
        assert "ARTIFACT_POLICY_EXTERNAL_REF" in errors[0]

    def test_external_ref_vague_manifest_fails(self):
        """Vague 'see R51 manifest' without prior_bundle_sha256 fails."""
        contract = {"installed_artifact_policy": "external_ref"}
        meta = {
            "package-artifact-manifest.yaml": "r51_artifact_status: unchanged_from_r51\n"
        }
        with _make_zf({}) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert len(errors) == 1
        assert "ARTIFACT_POLICY_EXTERNAL_REF" in errors[0]
        assert "prior_bundle_sha256" in errors[0]

    def test_external_ref_with_partial_manifest_fails(self):
        """Has prior_bundle_filename but missing prior_bundle_sha256."""
        contract = {"installed_artifact_policy": "external_ref"}
        meta = {
            "package-artifact-manifest.yaml": (
                "prior_bundle_filename: r51-bundle.zip\n"
                "# missing prior_bundle_sha256\n"
            )
        }
        with _make_zf({}) as zf:
            errors = check_installed_artifact_policy(contract, meta, zf)
        assert len(errors) == 1
        assert "prior_bundle_sha256" in errors[0]
