"""Report integrity tests for certification reports.

Validates all 210+ certification reports parse as valid JSON, contain
required fields, and are internally consistent with the portfolio matrix.

mission_id: CERT-INTEGRATION-HEALING-20260628
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CERT_ROOT = REPO_ROOT / "reports" / "certification"

EXPECTED_FORMATS = {
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt", "gnumeric",
    "ndjson", "ods", "odt", "pbm", "pgm", "ppm", "qoi", "sylk",
    "toml", "tsv", "xcf", "zst",
}

EXPECTED_REPORT_TYPES = {
    "api-contract.json",
    "traceability-audit.json",
    "stub-audit.json",
    "exception-audit.json",
    "oracle-alignment.json",
    "assertion-quality.json",
    "roundtrip-audit.json",
    "package-proof.json",
    "consumer-proof.json",
}

PLACEHOLDER_MARKERS = {"TODO", "FIXME", "PLACEHOLDER", "UNIMPLEMENTED", "TBD"}


def _all_json_files():
    """Yield all JSON files under reports/certification/."""
    for p in CERT_ROOT.rglob("*.json"):
        yield p


def _per_format_dirs():
    """Yield (format_id, dir_path) for each expected format."""
    for fmt in sorted(EXPECTED_FORMATS):
        fmt_dir = CERT_ROOT / fmt
        if fmt_dir.is_dir():
            yield fmt, fmt_dir


class TestAllReportsParseAsJson:
    """Every .json file under reports/certification/ must parse."""

    @pytest.fixture(scope="class")
    def json_files(self):
        return list(_all_json_files())

    def test_at_least_200_json_files_exist(self, json_files):
        assert len(json_files) >= 200, f"Only {len(json_files)} JSON files found"

    @pytest.mark.parametrize("json_path", list(_all_json_files()),
                             ids=lambda p: p.relative_to(CERT_ROOT).as_posix())
    def test_parses_as_valid_json(self, json_path):
        text = json_path.read_text(encoding="utf-8")
        data = json.loads(text)
        assert isinstance(data, (dict, list)), f"Unexpected JSON root type: {type(data)}"


class TestPerFormatReportCompleteness:
    """Each production format must have the expected report types."""

    @pytest.mark.parametrize("fmt,fmt_dir", list(_per_format_dirs()),
                             ids=lambda x: x if isinstance(x, str) else "")
    def test_format_has_required_reports(self, fmt, fmt_dir):
        present = {f.name for f in fmt_dir.iterdir() if f.suffix == ".json"}
        missing = EXPECTED_REPORT_TYPES - present
        assert not missing, f"{fmt} missing reports: {missing}"


class TestNoPlaceholderValues:
    """Reports must not contain placeholder values in verdict/status fields."""

    @pytest.mark.parametrize("json_path", list(_all_json_files()),
                             ids=lambda p: p.relative_to(CERT_ROOT).as_posix())
    def test_no_placeholder_in_status_fields(self, json_path):
        text = json_path.read_text(encoding="utf-8")
        data = json.loads(text)
        if not isinstance(data, dict):
            return
        for key in ("status", "overall_verdict", "alignment_status"):
            val = data.get(key, "")
            if isinstance(val, str):
                assert val.upper() not in PLACEHOLDER_MARKERS, \
                    f"{json_path.name}: {key}={val} is a placeholder"


class TestPortfolioMatrixConsistency:
    """portfolio-certification-matrix.json must be consistent with per-format reports."""

    @pytest.fixture(scope="class")
    def matrix(self):
        path = CERT_ROOT / "portfolio-certification-matrix.json"
        assert path.exists(), "portfolio-certification-matrix.json missing"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_matrix_has_20_formats(self, matrix):
        assert len(matrix.get("formats", [])) == 20

    def test_matrix_format_ids_match_expected(self, matrix):
        ids = {f["format_id"] for f in matrix["formats"]}
        assert ids == EXPECTED_FORMATS

    def test_matrix_summary_counts_add_up(self, matrix):
        s = matrix["portfolio_summary"]
        total = (s.get("certified", 0) + s.get("certified_with_gaps", 0) +
                 s.get("not_certified", 0) + s.get("in_progress", 0) +
                 s.get("not_started", 0))
        assert total == s["total_formats"], \
            f"Summary counts don't add up: {total} != {s['total_formats']}"

    def test_certified_formats_have_all_dimensions_pass(self, matrix):
        """CERTIFIED formats must have all non-N/A dimensions as PASS."""
        for entry in matrix["formats"]:
            if entry["overall_verdict"] != "CERTIFIED":
                continue
            dims = entry.get("dimensions", {})
            for dim_name, dim_data in dims.items():
                status = dim_data.get("status", "UNKNOWN")
                assert status in ("PASS", "NOT_APPLICABLE"), \
                    f"{entry['format_id']}: CERTIFIED but {dim_name}={status}"

    def test_no_certified_with_material_stubs(self, matrix):
        """CERTIFIED formats must have 0 material stubs."""
        for entry in matrix["formats"]:
            if entry["overall_verdict"] != "CERTIFIED":
                continue
            stubs = entry.get("dimensions", {}).get("stubs", {})
            mat_count = stubs.get("material_finding_count", 0)
            assert mat_count == 0, \
                f"{entry['format_id']}: CERTIFIED but has {mat_count} material stubs"

    def test_no_certified_with_uncovered_exceptions(self, matrix):
        """CERTIFIED formats must have 0 uncovered exceptions."""
        for entry in matrix["formats"]:
            if entry["overall_verdict"] != "CERTIFIED":
                continue
            exc = entry.get("dimensions", {}).get("exceptions", {})
            uncov = exc.get("uncovered_exception_count", exc.get("uncovered", 0))
            assert uncov == 0, \
                f"{entry['format_id']}: CERTIFIED but has {uncov} uncovered exceptions"
