"""
test_r166_sylk_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT7-001
Added: 2026-06-11

Tests for SYLK core functions: probe_sylk, parse_sylk, sylk_to_csv,
get_cell_value, get_row_values, get_row_count, get_column_count, get_cell_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import (
    probe_sylk,
    parse_sylk,
    parse_sylk_strict,
    sylk_to_csv,
    get_cell_value,
    get_row_values,
    get_row_count,
    get_column_count,
    get_cell_count,
    write_sylk,
    SylkDocument,
    SylkCell,
    SylkError,
    SylkInvalidFormatError,
)

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = _SAMPLES / "minimal-2x2.slk"
_NUMERIC = _SAMPLES / "numeric-row.slk"


def _make_sylk(tmp_path: Path, cells=None) -> Path:
    """Create a minimal SYLK file with given cells."""
    if cells is None:
        cells = [
            SylkCell(row=1, col=1, value=10),
            SylkCell(row=1, col=2, value=20),
            SylkCell(row=2, col=1, value="hello"),
            SylkCell(row=2, col=2, value=30.5),
        ]
    doc = SylkDocument(rows=2, cols=2, cells=cells)
    p = tmp_path / "test.slk"
    write_sylk(doc, p)
    return p


# ── Error classes ──────────────────────────────────────────────────────────

class TestSylkErrors:

    def test_sylk_error_is_exception(self):
        assert isinstance(SylkError("x"), Exception)

    def test_sylk_invalid_format_inherits(self):
        assert isinstance(SylkInvalidFormatError("x"), SylkError)


# ── probe_sylk ─────────────────────────────────────────────────────────────

class TestProbeSylk:

    def test_returns_dict(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = probe_sylk(p)
        assert isinstance(result, dict)

    def test_exists_true(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = probe_sylk(p)
        assert result.get("exists") is True

    def test_nonexistent_file(self, tmp_path):
        result = probe_sylk(tmp_path / "no_such.slk")
        assert result.get("exists") is False

    def test_has_path_key(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = probe_sylk(p)
        assert "path" in result

    def test_valid_sylk_detected(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = probe_sylk(p)
        assert result.get("valid_header") is True


# ── parse_sylk ─────────────────────────────────────────────────────────────

class TestParseSylk:

    def test_returns_dict(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = parse_sylk(p)
        assert isinstance(result, dict)

    def test_ok_key(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = parse_sylk(p)
        assert result.get("ok") is True

    def test_nonexistent_returns_error(self, tmp_path):
        result = parse_sylk(tmp_path / "nope.slk")
        assert "error" in result

    def test_sample_file(self):
        result = parse_sylk(_MINIMAL)
        assert isinstance(result, dict)

    def test_strict_parses_sample(self):
        doc = parse_sylk_strict(_MINIMAL)
        assert doc.rows == 2
        assert doc.cols == 2


# ── sylk_to_csv ────────────────────────────────────────────────────────────

class TestSylkToCsv:

    def test_returns_string(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = sylk_to_csv(p)
        assert isinstance(result, str)

    def test_contains_values(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = sylk_to_csv(p)
        assert "10" in result

    def test_comma_separated(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = sylk_to_csv(p)
        assert "," in result

    def test_from_sample(self):
        result = sylk_to_csv(_NUMERIC)
        assert isinstance(result, str)


# ── get_cell_value ─────────────────────────────────────────────────────────

class TestGetCellValue:

    def test_returns_value(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_cell_value(p, row=1, col=1)
        assert result == 10

    def test_string_cell(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_cell_value(p, row=2, col=1)
        assert result == "hello"

    def test_float_cell(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_cell_value(p, row=2, col=2)
        assert result == 30.5


# ── get_row_values ─────────────────────────────────────────────────────────

class TestGetRowValues:

    def test_returns_list(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_row_values(p, row=1)
        assert isinstance(result, list)

    def test_row_has_values(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_row_values(p, row=1)
        assert 10 in result
        assert 20 in result


# ── get_row_count / get_column_count / get_cell_count ─────────────────────

class TestCounts:

    def test_row_count(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_row_count(p)
        assert result == 2

    def test_column_count(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_column_count(p)
        assert result == 2

    def test_cell_count(self, tmp_path):
        p = _make_sylk(tmp_path)
        result = get_cell_count(p)
        assert result == 4
