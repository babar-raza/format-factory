"""Tests for FreezeGateRunner — Pilot 3 freeze gate verification.

Taskcard: LFI-3-B01
Sprint: FF-LIBFORGE-BROAD-IMPLEMENTATION-001
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from tools.supervisor.freeze_gate_runner import (
    FreezeGateRunner,
    GateKind,
    GateResult,
    GateStatus,
    RunReport,
)


@pytest.fixture
def runner():
    return FreezeGateRunner(repo_root=str(_REPO_ROOT))


# ---------------------------------------------------------------------------
# GateResult dataclass
# ---------------------------------------------------------------------------


class TestGateResult:
    def test_to_dict(self):
        r = GateResult(
            gate_id="ZST-TEST",
            gate_kind="binding_roundtrip",
            format_id="zst",
            status="PASS",
        )
        d = r.to_dict()
        assert d["gate_id"] == "ZST-TEST"
        assert d["status"] == "PASS"

    def test_to_json_serializable(self):
        r = GateResult(
            gate_id="ZST-TEST",
            gate_kind="contract_validation",
            format_id="zst",
            status="PASS",
            description="OK",
        )
        parsed = json.loads(r.to_json())
        assert parsed["status"] == "PASS"

    def test_all_statuses_are_valid_json(self):
        for status in GateStatus:
            r = GateResult(
                gate_id="X", gate_kind="binding_roundtrip", format_id="zst",
                status=status.value
            )
            json.loads(r.to_json())


# ---------------------------------------------------------------------------
# RunReport
# ---------------------------------------------------------------------------


class TestRunReport:
    def test_overall_status_pass(self):
        r = RunReport(run_id="test", format_id="zst", gates_run=1, passed=1)
        assert r.overall_status == "PASS"

    def test_overall_status_fail(self):
        r = RunReport(run_id="test", format_id="zst", gates_run=1, failed=1)
        assert r.overall_status == "FAIL"

    def test_overall_status_error_takes_priority(self):
        r = RunReport(run_id="test", format_id="zst", gates_run=2, passed=1, errors=1)
        assert r.overall_status == "ERROR"

    def test_to_json(self):
        r = RunReport(run_id="x", format_id="zst")
        parsed = json.loads(r.to_json())
        assert "overall_status" in parsed
        assert "results" in parsed


# ---------------------------------------------------------------------------
# Unsupported format/gate kind
# ---------------------------------------------------------------------------


class TestUnsupportedFormat:
    def test_unsupported_format_returns_error(self, runner):
        report = runner.run("xyzfake", run_id="test")
        assert report.overall_status == "ERROR"
        assert report.gates_run == 1
        assert report.errors == 1
        assert "unsupported" in report.results[0].error.lower()

    def test_unsupported_gate_kind_returns_error(self, runner):
        report = runner.run("zst", gate_kinds=["nonexistent_gate"], run_id="test")
        assert report.overall_status == "ERROR"
        assert report.errors == 1


# ---------------------------------------------------------------------------
# ZST binding_roundtrip — happy path
# ---------------------------------------------------------------------------


class TestZstBindingRoundtrip:
    def test_synthetic_fixture_passes(self, runner):
        report = runner.run(
            "zst",
            gate_kinds=["binding_roundtrip"],
            run_id="test-roundtrip",
        )
        assert report.overall_status == "PASS", f"Unexpected: {report.results[0].error}"
        assert report.passed == 1
        result = report.results[0]
        assert result.status == GateStatus.PASS.value
        assert result.sha256_in is not None
        assert result.sha256_out is not None
        assert result.sha256_in == result.sha256_out  # identity

    def test_result_has_fact_citation(self, runner):
        report = runner.run("zst", gate_kinds=["binding_roundtrip"])
        result = report.results[0]
        assert result.fact_id == "FACT-ZST-001"

    def test_result_has_compression_metadata(self, runner):
        report = runner.run("zst", gate_kinds=["binding_roundtrip"])
        result = report.results[0]
        assert "compression_ratio" in result.metadata
        assert result.metadata["compression_ratio"] > 0

    def test_idempotent_rerun_produces_same_status(self, runner):
        r1 = runner.run("zst", gate_kinds=["binding_roundtrip"])
        r2 = runner.run("zst", gate_kinds=["binding_roundtrip"])
        assert r1.overall_status == r2.overall_status
        assert r1.results[0].sha256_in == r2.results[0].sha256_in

    def test_file_fixture_passes(self, runner):
        """Valid ZST file fixture round-trips correctly."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Hello from file fixture test!\n" * 10)
            tmp_path = f.name
        report = runner.run("zst", gate_kinds=["binding_roundtrip"], fixture_path=tmp_path)
        assert report.overall_status == "PASS"

    def test_missing_fixture_fails(self, runner):
        """Non-existent fixture file produces FAIL, not ERROR."""
        report = runner.run(
            "zst",
            gate_kinds=["binding_roundtrip"],
            fixture_path="/nonexistent/path/fixture.bin",
        )
        result = report.results[0]
        assert result.status == GateStatus.FAIL.value
        assert "not found" in result.description.lower() or "missing" in result.error.lower()

    def test_corrupted_fixture_still_roundtrips(self, runner):
        """Arbitrary binary content (not valid ZST) still round-trips via compress/decompress."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            # Write known non-ZST content; compress_bytes can still compress arbitrary bytes
            f.write(b"\x00\xFF\xAB\xCD" * 50 + b"corrupt-data")
            tmp_path = f.name
        report = runner.run("zst", gate_kinds=["binding_roundtrip"], fixture_path=tmp_path)
        # compress_bytes accepts arbitrary bytes — should still pass identity
        assert report.overall_status == "PASS", f"Expected PASS, got: {report.results[0].error}"
        assert report.results[0].sha256_in == report.results[0].sha256_out

    def test_empty_fixture_roundtrips(self, runner):
        """Empty fixture file round-trips without error."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(b"")
            tmp_path = f.name
        report = runner.run("zst", gate_kinds=["binding_roundtrip"], fixture_path=tmp_path)
        # compress_bytes on empty bytes may work — check it doesn't ERROR
        assert report.results[0].status in (
            GateStatus.PASS.value, GateStatus.FAIL.value
        ), f"Unexpected ERROR on empty fixture: {report.results[0].error}"


# ---------------------------------------------------------------------------
# ZST contract_validation
# ---------------------------------------------------------------------------


class TestZstContractValidation:
    def test_magic_bytes_pass(self, runner):
        report = runner.run("zst", gate_kinds=["contract_validation"])
        assert report.overall_status == "PASS"
        result = report.results[0]
        assert result.status == GateStatus.PASS.value
        assert result.fact_id == "FACT-ZST-001"

    def test_fact_002_not_applicable_yet(self, runner):
        """FACT-ZST-002 is reported NOT_APPLICABLE_YET, not a fake pass."""
        report = runner.run("zst", gate_kinds=["contract_validation"])
        result = report.results[0]
        assert "NOT_APPLICABLE_YET" in result.detail or "NOT_APPLICABLE_YET" in str(result.metadata)

    def test_result_has_magic_metadata(self, runner):
        report = runner.run("zst", gate_kinds=["contract_validation"])
        result = report.results[0]
        assert "ZSTD_MAGIC" in result.metadata
        assert result.metadata["magic_verified"] is True

    def test_result_is_json_serializable(self, runner):
        report = runner.run("zst", gate_kinds=["contract_validation"])
        json.loads(report.to_json())


# ---------------------------------------------------------------------------
# Combined run (both gates)
# ---------------------------------------------------------------------------


class TestCombinedRun:
    def test_both_gates_pass(self, runner):
        report = runner.run("zst")
        assert report.gates_run == 2
        assert report.passed == 2
        assert report.overall_status == "PASS"

    def test_full_report_serializable(self, runner):
        report = runner.run("zst", run_id="combined-test")
        d = report.to_dict()
        assert d["run_id"] == "combined-test"
        assert len(d["results"]) == 2
        json.dumps(d)  # must not raise


# ---------------------------------------------------------------------------
# NDJSON gates — v2 second format (LFI-6-B)
# ---------------------------------------------------------------------------


class TestNdjsonSupportedFormat:
    def test_ndjson_in_supported_formats(self, runner):
        assert "ndjson" in runner.SUPPORTED_FORMATS

    def test_ndjson_binding_roundtrip_passes(self, runner):
        report = runner.run("ndjson", gate_kinds=["binding_roundtrip"])
        assert report.overall_status == GateStatus.PASS.value
        assert report.passed == 1

    def test_ndjson_binding_roundtrip_has_identity_detail(self, runner):
        report = runner.run("ndjson", gate_kinds=["binding_roundtrip"])
        result = report.results[0]
        assert "identity=true" in result.detail
        assert result.metadata["identity"] is True

    def test_ndjson_binding_roundtrip_has_record_metadata(self, runner):
        report = runner.run("ndjson", gate_kinds=["binding_roundtrip"])
        result = report.results[0]
        assert "record_count" in result.metadata
        assert result.metadata["record_count"] == 3

    def test_ndjson_contract_validation_not_applicable(self, runner):
        report = runner.run("ndjson", gate_kinds=["contract_validation"])
        result = report.results[0]
        assert result.status == GateStatus.NOT_APPLICABLE.value

    def test_ndjson_contract_validation_explains_why(self, runner):
        report = runner.run("ndjson", gate_kinds=["contract_validation"])
        result = report.results[0]
        assert "FACT-NDJSON-001" in result.description or "FACT-NDJSON-001" in result.detail

    def test_ndjson_full_run_has_pass_and_not_applicable(self, runner):
        """Running both gates: binding_roundtrip=PASS, contract_validation=NOT_APPLICABLE."""
        report = runner.run("ndjson")
        assert report.gates_run == 2
        assert report.passed == 1
        assert report.not_applicable == 1
        # Overall: no errors, no failures → PASS
        assert report.overall_status == GateStatus.PASS.value

    def test_ndjson_report_is_json_serializable(self, runner):
        report = runner.run("ndjson", run_id="ndjson-lane-b-test")
        d = report.to_dict()
        assert d["format_id"] == "ndjson"
        json.dumps(d)  # must not raise

    def test_ndjson_result_sha256_populated(self, runner):
        report = runner.run("ndjson", gate_kinds=["binding_roundtrip"])
        result = report.results[0]
        assert result.sha256_in is not None
        assert result.sha256_out is not None
        assert len(result.sha256_in) == 64  # SHA-256 hex
