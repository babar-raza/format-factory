"""Tests for governance_validators_certification.py (V_CERT_01-V_CERT_05).

TC-007 (precious-wandering-lighthouse, 2026-07-13).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators_certification import (
    validate_all_evidence_present_for_certified_formats,
    validate_no_certified_format_has_material_stubs,
    validate_certification_run_manifests_exist,
    validate_certification_layer_registered,
    validate_gap_reconciliation_map_exists,
)


_DECL: dict = {}

_DIMENSION_REPORTS = [
    "api-contract.json", "traceability-audit.json", "stub-audit.json",
    "exception-audit.json", "oracle-alignment.json", "assertion-quality.json",
    "roundtrip-audit.json", "package-proof.json", "consumer-proof.json",
]


def _make_matrix(fmt: str, verdict: str, cert_root: Path) -> None:
    matrix = {
        "formats": [{"format_id": fmt, "overall_verdict": verdict}]
    }
    (cert_root / "portfolio-certification-matrix.json").write_text(json.dumps(matrix))


class TestVCert01AllEvidencePresent:

    def test_pass_when_all_9_reports_present(self, tmp_path):
        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "csv"
        fmt_dir.mkdir(parents=True)
        for report in _DIMENSION_REPORTS:
            (fmt_dir / report).write_text("{}")
        _make_matrix("csv", "CERTIFIED", cert_root)

        result = validate_all_evidence_present_for_certified_formats(
            _DECL, tmp_path
        )
        assert result["result"] == "PASS"

    def test_warn_when_report_missing(self, tmp_path):
        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "csv"
        fmt_dir.mkdir(parents=True)
        # Only 8 of 9 reports
        for report in _DIMENSION_REPORTS[:-1]:
            (fmt_dir / report).write_text("{}")
        _make_matrix("csv", "CERTIFIED", cert_root)

        result = validate_all_evidence_present_for_certified_formats(
            _DECL, tmp_path
        )
        assert result["result"] == "WARN", (
            f"Expected WARN when a report is missing; got {result['result']}"
        )
        assert "consumer-proof.json" in result["message"]

    def test_skip_when_no_matrix(self, tmp_path):
        result = validate_all_evidence_present_for_certified_formats(
            _DECL, tmp_path
        )
        assert result["result"] == "SKIP"


class TestVCert02NoMaterialStubs:

    def test_pass_when_no_stubs(self, tmp_path):
        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "csv"
        fmt_dir.mkdir(parents=True)
        (fmt_dir / "stub-audit.json").write_text(json.dumps({"material_finding_count": 0}))
        _make_matrix("csv", "CERTIFIED", cert_root)

        result = validate_no_certified_format_has_material_stubs(_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_fail_when_certified_format_has_material_stubs(self, tmp_path):
        """V_CERT_02: manually-injected stub finding must cause FAIL."""
        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "csv"
        fmt_dir.mkdir(parents=True)
        # Inject: 1 material stub
        (fmt_dir / "stub-audit.json").write_text(json.dumps({"material_finding_count": 1}))
        _make_matrix("csv", "CERTIFIED", cert_root)

        result = validate_no_certified_format_has_material_stubs(_DECL, tmp_path)
        assert result["result"] == "FAIL", (
            f"V_CERT_02 must FAIL when CERTIFIED format has material stubs; "
            f"got {result['result']}. message: {result['message']}"
        )
        assert "csv" in result["message"]

    def test_ignore_non_certified_formats(self, tmp_path):
        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "csv"
        fmt_dir.mkdir(parents=True)
        # 5 material stubs but format is IN_PROGRESS, not CERTIFIED
        (fmt_dir / "stub-audit.json").write_text(json.dumps({"material_finding_count": 5}))
        _make_matrix("csv", "IN_PROGRESS", cert_root)

        result = validate_no_certified_format_has_material_stubs(_DECL, tmp_path)
        assert result["result"] == "PASS"


class TestVCert03RunManifestsExist:

    def test_pass_when_manifest_present(self, tmp_path):
        cert_root = tmp_path / "reports" / "certification"
        run_dir = cert_root / "runs" / "cert-initial-crispy-jingling-snail"
        run_dir.mkdir(parents=True)
        (run_dir / "csv-manifest.json").write_text(json.dumps({"run_id": "cert-initial-crispy-jingling-snail"}))
        _make_matrix("csv", "CERTIFIED", cert_root)

        result = validate_certification_run_manifests_exist(_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_warn_when_no_manifest_for_certified(self, tmp_path):
        cert_root = tmp_path / "reports" / "certification"
        # runs/ exists but no manifest for csv
        (cert_root / "runs" / "some-run").mkdir(parents=True)
        _make_matrix("csv", "CERTIFIED", cert_root)

        result = validate_certification_run_manifests_exist(_DECL, tmp_path)
        assert result["result"] == "WARN"
        assert "csv" in result["message"]


class TestVCert04CertificationLayerRegistered:

    def test_pass_when_l28_at_maturity_4(self, tmp_path):
        layers_dir = tmp_path / "plans" / "layers"
        layers_dir.mkdir(parents=True)
        (layers_dir / "index.yaml").write_text(
            "- layer_id: L28\n  maturity_current: 4\n  maturity_target: 5\n"
        )

        result = validate_certification_layer_registered(_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_fail_when_l28_missing(self, tmp_path):
        layers_dir = tmp_path / "plans" / "layers"
        layers_dir.mkdir(parents=True)
        (layers_dir / "index.yaml").write_text("- layer_id: L01\n  maturity_current: 5\n")

        result = validate_certification_layer_registered(_DECL, tmp_path)
        assert result["result"] == "FAIL"

    def test_fail_when_maturity_below_4(self, tmp_path):
        layers_dir = tmp_path / "plans" / "layers"
        layers_dir.mkdir(parents=True)
        (layers_dir / "index.yaml").write_text(
            "- layer_id: L28\n  maturity_current: 3\n  maturity_target: 5\n"
        )

        result = validate_certification_layer_registered(_DECL, tmp_path)
        assert result["result"] == "FAIL"
        assert "3" in result["message"]


class TestVCert05GapReconciliationMapExists:

    def test_pass_when_v2_map_exists(self, tmp_path):
        ci_dir = tmp_path / "reports" / "certification-integration"
        ci_dir.mkdir(parents=True)
        (ci_dir / "gap-reconciliation-map-v2.yaml").write_text(
            "total_findings: 5\ndispositions: []\n"
        )

        result = validate_gap_reconciliation_map_exists(_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_warn_when_only_v1_exists(self, tmp_path):
        ci_dir = tmp_path / "reports" / "certification-integration"
        ci_dir.mkdir(parents=True)
        (ci_dir / "gap-reconciliation-map.yaml").write_text("gap_reconciliation_map:\n  reconciliation_verdict: CLEAN\n")

        result = validate_gap_reconciliation_map_exists(_DECL, tmp_path)
        assert result["result"] == "WARN"

    def test_fail_when_no_map_exists(self, tmp_path):
        result = validate_gap_reconciliation_map_exists(_DECL, tmp_path)
        assert result["result"] == "FAIL"
