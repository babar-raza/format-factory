"""
Tests for capability_verifier.py — 4-Bucket Capability Verification

Taskcard: LFI-E-002
Run ID: ff-libforge-integration-exec-20260610-133949

Tests use synthetic temp fixtures — no dependency on actual product source.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.capability_verifier import (
    CapabilityVerifier,
    FormatMissing,
    SignatureDrift,
    StaleTest,
    Untested,
    VerificationReport,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cap_map(capabilities):
    """Build a minimal unified-capability-map.json dict."""
    return {
        "schema_version": "1.0",
        "capabilities": capabilities,
    }


def _foss_cap(format_id, capability_name, operation_kind=None):
    """Build a minimal FOSS capability record."""
    return {
        "capability_id": f"{format_id.upper()}-FOSS-{(operation_kind or capability_name).upper()}-001",
        "format": format_id.upper(),
        "product_type": "foss_reduced",
        "capability_name": capability_name,
        "operation_kind": operation_kind or capability_name.lower().replace(" ", "_"),
    }


def _write_init(source_dir, all_names):
    """Write an __init__.py with __all__ and matching imports."""
    init = source_dir / "__init__.py"
    lines = [f"from .codec import {', '.join(all_names)}", f"__all__ = {all_names!r}"]
    init.write_text("\n".join(lines), encoding="utf-8")


def _write_codec(source_dir, func_names):
    """Write a codec.py with function stubs."""
    codec = source_dir / "codec.py"
    lines = []
    for name in func_names:
        if name[0].isupper():
            lines.append(f"class {name}: pass")
        else:
            lines.append(f"def {name}(): pass")
    codec.write_text("\n".join(lines), encoding="utf-8")


def _write_test(test_dir, filename, imports):
    """Write a test file that imports specific names."""
    test_file = test_dir / filename
    lines = [f"from somewhere import {', '.join(imports)}", "def test_placeholder(): pass"]
    test_file.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Test: Import
# ---------------------------------------------------------------------------

class TestImport:
    def test_can_import_capability_verifier(self):
        assert CapabilityVerifier is not None

    def test_can_import_report(self):
        assert VerificationReport is not None

    def test_can_import_bucket_types(self):
        assert FormatMissing is not None
        assert Untested is not None
        assert SignatureDrift is not None
        assert StaleTest is not None


# ---------------------------------------------------------------------------
# Test: FORMAT_MISSING bucket
# ---------------------------------------------------------------------------

class TestFormatMissing:
    def test_missing_source_directory(self, tmp_path):
        """Capability record exists for 'xyz' format but src/python/xyz/ does not."""
        cap_map = _make_cap_map([_foss_cap("XYZ", "Load", "load")])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        source_root.mkdir()
        test_root = tmp_path / "tests"
        test_root.mkdir()

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        assert len(report.format_missing) == 1
        assert report.format_missing[0].format_id == "xyz"
        assert report.format_missing[0].capability_name == "Load"
        assert not report.passed

    def test_existing_source_directory_no_missing(self, tmp_path):
        """Source directory exists — should NOT be FORMAT_MISSING."""
        cap_map = _make_cap_map([_foss_cap("ABW", "load", "load")])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "abw"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["load"])
        _write_codec(fmt_dir, ["load"])

        test_root = tmp_path / "tests"
        test_dir = test_root / "abw"
        test_dir.mkdir(parents=True)
        _write_test(test_dir, "test_load.py", ["load"])

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        assert len(report.format_missing) == 0


# ---------------------------------------------------------------------------
# Test: UNTESTED bucket
# ---------------------------------------------------------------------------

class TestUntested:
    def test_exported_but_not_tested(self, tmp_path):
        """Function in __all__ but not imported in any test file."""
        cap_map = _make_cap_map([_foss_cap("ABW", "load", "load")])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "abw"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["load", "export_csv", "get_stats"])
        _write_codec(fmt_dir, ["load", "export_csv", "get_stats"])

        test_root = tmp_path / "tests"
        test_dir = test_root / "abw"
        test_dir.mkdir(parents=True)
        _write_test(test_dir, "test_load.py", ["load"])

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        untested_names = {u.function_name for u in report.untested}
        assert "export_csv" in untested_names
        assert "get_stats" in untested_names
        assert "load" not in untested_names

    def test_classes_excluded_from_untested(self, tmp_path):
        """Classes/exceptions in __all__ should NOT be flagged as UNTESTED."""
        cap_map = _make_cap_map([])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "abw"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["AbwError", "load"])
        _write_codec(fmt_dir, ["AbwError", "load"])

        test_root = tmp_path / "tests"
        test_dir = test_root / "abw"
        test_dir.mkdir(parents=True)
        _write_test(test_dir, "test_load.py", ["load"])

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        untested_names = {u.function_name for u in report.untested}
        assert "AbwError" not in untested_names

    def test_no_test_directory(self, tmp_path):
        """No test dir at all — all functions flagged as UNTESTED."""
        cap_map = _make_cap_map([])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "abw"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["load", "save"])
        _write_codec(fmt_dir, ["load", "save"])

        test_root = tmp_path / "tests"
        test_root.mkdir()
        # No abw/ test subdir

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        untested_names = {u.function_name for u in report.untested}
        assert "load" in untested_names
        assert "save" in untested_names


# ---------------------------------------------------------------------------
# Test: SIGNATURE_DRIFT bucket
# ---------------------------------------------------------------------------

class TestSignatureDrift:
    def test_cap_function_not_in_source(self, tmp_path):
        """Capability map says 'compress' exists but source doesn't export it."""
        cap_map = _make_cap_map([_foss_cap("ZST", "compress", "compress")])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "zst"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["decompress"])  # 'compress' missing
        _write_codec(fmt_dir, ["decompress"])

        test_root = tmp_path / "tests"
        test_root.mkdir()

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        assert len(report.signature_drift) == 1
        assert report.signature_drift[0].expected_function == "compress"
        assert report.signature_drift[0].format_id == "zst"

    def test_cap_function_present_no_drift(self, tmp_path):
        """Capability map says 'compress' and source exports it — no drift."""
        cap_map = _make_cap_map([_foss_cap("ZST", "compress", "compress")])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "zst"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["compress", "decompress"])
        _write_codec(fmt_dir, ["compress", "decompress"])

        test_root = tmp_path / "tests"
        test_root.mkdir()

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        assert len(report.signature_drift) == 0


# ---------------------------------------------------------------------------
# Test: STALE_TEST bucket
# ---------------------------------------------------------------------------

class TestStaleTest:
    def test_test_imports_removed_function(self, tmp_path):
        """Test file imports 'old_func' which is no longer in source exports."""
        cap_map = _make_cap_map([])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "abw"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["load"])
        _write_codec(fmt_dir, ["load"])

        test_root = tmp_path / "tests"
        test_dir = test_root / "abw"
        test_dir.mkdir(parents=True)
        _write_test(test_dir, "test_old.py", ["old_func", "load"])

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        stale_names = {s.function_name for s in report.stale_test}
        assert "old_func" in stale_names
        assert "load" not in stale_names

    def test_no_stale_when_all_imports_valid(self, tmp_path):
        """All test imports match source exports — no stale tests."""
        cap_map = _make_cap_map([])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "abw"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["load", "save"])
        _write_codec(fmt_dir, ["load", "save"])

        test_root = tmp_path / "tests"
        test_dir = test_root / "abw"
        test_dir.mkdir(parents=True)
        _write_test(test_dir, "test_load.py", ["load", "save"])

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        assert len(report.stale_test) == 0


# ---------------------------------------------------------------------------
# Test: JSON serialization
# ---------------------------------------------------------------------------

class TestJsonSerialization:
    def test_empty_report_serializes(self):
        report = VerificationReport()
        j = report.to_json()
        data = json.loads(j)
        assert data["passed"] is True
        assert data["summary"]["format_missing_count"] == 0

    def test_report_with_findings_serializes(self, tmp_path):
        """Report with findings serializes correctly."""
        report = VerificationReport()
        report.format_missing.append(
            FormatMissing(format_id="xyz", capability_id="XYZ-001", capability_name="Load")
        )
        report.untested.append(
            Untested(format_id="abw", function_name="save", source_module="/src/abw")
        )

        j = report.to_json()
        data = json.loads(j)
        assert data["passed"] is False
        assert data["summary"]["format_missing_count"] == 1
        assert data["summary"]["untested_count"] == 1
        assert data["format_missing"][0]["format_id"] == "xyz"
        assert data["untested"][0]["function_name"] == "save"

    def test_json_roundtrip_valid(self):
        """JSON output is valid JSON and re-parseable."""
        report = VerificationReport()
        report.signature_drift.append(
            SignatureDrift(
                format_id="zst", capability_id="ZST-001",
                capability_name="compress", expected_function="compress"
            )
        )
        data = json.loads(report.to_json())
        assert isinstance(data, dict)
        assert "signature_drift" in data


# ---------------------------------------------------------------------------
# Test: passed property
# ---------------------------------------------------------------------------

class TestPassedProperty:
    def test_empty_report_passes(self):
        assert VerificationReport().passed is True

    def test_any_finding_fails(self):
        r = VerificationReport()
        r.stale_test.append(StaleTest("x", "f", "t.py"))
        assert r.passed is False


# ---------------------------------------------------------------------------
# Test: No product source writes
# ---------------------------------------------------------------------------

class TestNoProductSourceWrites:
    def test_verify_does_not_write_to_source(self, tmp_path):
        """Verify that running the verifier does not create or modify files in source."""
        cap_map = _make_cap_map([_foss_cap("ABW", "load", "load")])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        fmt_dir = source_root / "abw"
        fmt_dir.mkdir(parents=True)
        _write_init(fmt_dir, ["load"])
        _write_codec(fmt_dir, ["load"])

        test_root = tmp_path / "tests"
        test_root.mkdir()

        # Record file state before
        before = {p: p.stat().st_mtime for p in source_root.rglob("*") if p.is_file()}

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        verifier.verify()

        # Verify no new files and no modifications
        after_files = set(source_root.rglob("*"))
        for p in after_files:
            if p.is_file():
                assert p in before, f"New file created in source: {p}"
                assert p.stat().st_mtime == before[p], f"File modified in source: {p}"


# ---------------------------------------------------------------------------
# Test: Missing capability map
# ---------------------------------------------------------------------------

class TestMissingInputs:
    def test_missing_capability_map_file(self, tmp_path):
        """Non-existent capability map produces FORMAT_MISSING for ALL."""
        source_root = tmp_path / "src"
        source_root.mkdir()
        test_root = tmp_path / "tests"
        test_root.mkdir()

        verifier = CapabilityVerifier(
            tmp_path / "nonexistent.json", source_root, test_root
        )
        report = verifier.verify()

        assert len(report.format_missing) == 1
        assert report.format_missing[0].format_id == "ALL"
        assert not report.passed

    def test_malformed_json(self, tmp_path):
        """Malformed JSON produces FORMAT_MISSING for ALL."""
        cap_file = tmp_path / "bad.json"
        cap_file.write_text("{bad json", encoding="utf-8")

        source_root = tmp_path / "src"
        source_root.mkdir()
        test_root = tmp_path / "tests"
        test_root.mkdir()

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        assert len(report.format_missing) == 1
        assert not report.passed


# ---------------------------------------------------------------------------
# Test: Commercial capabilities are ignored
# ---------------------------------------------------------------------------

class TestCommercialFiltering:
    def test_commercial_caps_not_scanned(self, tmp_path):
        """Only foss_reduced capabilities are scanned; commercial are ignored."""
        cap_map = _make_cap_map([
            {
                "capability_id": "FODS-COMMERCIAL-LOAD-001",
                "format": "FODS",
                "product_type": "commercial",
                "capability_name": "Load",
                "operation_kind": "load",
            },
        ])
        cap_file = tmp_path / "cap.json"
        cap_file.write_text(json.dumps(cap_map), encoding="utf-8")

        source_root = tmp_path / "src"
        source_root.mkdir()
        test_root = tmp_path / "tests"
        test_root.mkdir()
        # No fods/ source dir — but should not be flagged since it's commercial

        verifier = CapabilityVerifier(cap_file, source_root, test_root)
        report = verifier.verify()

        assert report.passed  # No FOSS caps → empty report → passed


# ---------------------------------------------------------------------------
# Test: Real capability map (integration, against actual project files)
# ---------------------------------------------------------------------------

class TestRealCapabilityMap:
    """Optional integration test against the real project files.

    These tests only run if the real files exist (skipped in CI without project).
    """

    @pytest.mark.skipif(
        not (_REPO / "reports/capability-layer/unified-capability-map.json").exists(),
        reason="Real capability map not available",
    )
    def test_real_map_loads_and_produces_report(self):
        verifier = CapabilityVerifier(
            _REPO / "reports/capability-layer/unified-capability-map.json",
            _REPO / "src/python",
            _REPO / "tests/python",
        )
        report = verifier.verify()
        data = json.loads(report.to_json())

        # Report should be valid JSON with all expected keys
        assert "passed" in data
        assert "summary" in data
        assert isinstance(data["summary"]["format_missing_count"], int)
        assert isinstance(data["summary"]["untested_count"], int)
        assert isinstance(data["summary"]["signature_drift_count"], int)
        assert isinstance(data["summary"]["stale_test_count"], int)


# ---------------------------------------------------------------------------
# Test: product_selection_helper — v2 (LFI-6-E)
# ---------------------------------------------------------------------------


class TestProductSelectionHelper:
    """Tests for CapabilityVerifier.product_selection_helper() static method."""

    def _make_report(
        self,
        untested=None,
        signature_drift=None,
    ) -> VerificationReport:
        report = VerificationReport()
        if untested:
            report.untested.extend(untested)
        if signature_drift:
            report.signature_drift.extend(signature_drift)
        return report

    def test_empty_report_returns_empty_list(self):
        report = VerificationReport()
        candidates = CapabilityVerifier.product_selection_helper(report)
        assert candidates == []

    def test_untested_returned_as_priority_1(self):
        report = self._make_report(
            untested=[Untested(format_id="csv", function_name="read_csv", source_module="src/python/csv")]
        )
        candidates = CapabilityVerifier.product_selection_helper(report)
        assert len(candidates) == 1
        assert candidates[0]["priority"] == 1
        assert candidates[0]["bucket"] == "UNTESTED"
        assert candidates[0]["function_name"] == "read_csv"

    def test_signature_drift_returned_as_priority_2(self):
        report = self._make_report(
            signature_drift=[SignatureDrift(
                format_id="csv", capability_id="C1",
                capability_name="write_csv", expected_function="write_csv"
            )]
        )
        candidates = CapabilityVerifier.product_selection_helper(report)
        assert len(candidates) == 1
        assert candidates[0]["priority"] == 2
        assert candidates[0]["bucket"] == "SIGNATURE_DRIFT"

    def test_untested_prioritized_over_signature_drift(self):
        report = self._make_report(
            untested=[Untested(format_id="zst", function_name="compress", source_module="src")],
            signature_drift=[SignatureDrift(
                format_id="abw", capability_id="C1",
                capability_name="load", expected_function="load_abw"
            )],
        )
        candidates = CapabilityVerifier.product_selection_helper(report)
        assert candidates[0]["priority"] == 1
        assert candidates[1]["priority"] == 2

    def test_sorted_by_format_id_within_same_priority(self):
        report = self._make_report(
            untested=[
                Untested(format_id="zst", function_name="compress", source_module="src"),
                Untested(format_id="abw", function_name="load", source_module="src"),
            ]
        )
        candidates = CapabilityVerifier.product_selection_helper(report)
        assert candidates[0]["format_id"] == "abw"
        assert candidates[1]["format_id"] == "zst"

    def test_max_candidates_respected(self):
        report = self._make_report(
            untested=[
                Untested(format_id="fmt", function_name=f"fn_{i}", source_module="src")
                for i in range(10)
            ]
        )
        candidates = CapabilityVerifier.product_selection_helper(report, max_candidates=3)
        assert len(candidates) == 3

    def test_result_has_required_fields(self):
        report = self._make_report(
            untested=[Untested(format_id="csv", function_name="parse", source_module="src")]
        )
        candidates = CapabilityVerifier.product_selection_helper(report)
        c = candidates[0]
        assert "format_id" in c
        assert "function_name" in c
        assert "priority" in c
        assert "bucket" in c

    def test_result_is_json_serializable(self):
        report = self._make_report(
            untested=[Untested(format_id="csv", function_name="parse", source_module="src")],
            signature_drift=[SignatureDrift(
                format_id="csv", capability_id="C1",
                capability_name="write", expected_function="write_csv"
            )],
        )
        candidates = CapabilityVerifier.product_selection_helper(report)
        json.dumps(candidates)  # must not raise
