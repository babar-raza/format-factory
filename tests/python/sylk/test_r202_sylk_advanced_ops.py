"""
tests/python/sylk/test_r202_sylk_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT17-001
TASK-001 (part A): SYLK advanced operations.

Covers: parse_sylk, probe_sylk, get_capabilities, get_row_count, get_cell_count,
get_column_count, sylk_row_count, sylk_numeric_cell_count, sylk_string_cell_count,
sylk_empty_cell_count, sylk_total_sum, count_nonempty_cells, get_all_values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    parse_sylk, probe_sylk, get_capabilities,
    get_row_count, get_cell_count, get_column_count,
    sylk_row_count, sylk_numeric_cell_count, sylk_string_cell_count,
    sylk_empty_cell_count, sylk_total_sum, count_nonempty_cells,
    get_all_values,
)

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.slk")
_NUMERIC = str(_SAMPLES / "numeric-row.slk")
_SINGLE = str(_SAMPLES / "single-cell.slk")


class TestSylkParseAndProbe:
    """parse_sylk, probe_sylk, get_capabilities."""

    def test_parse_sylk_returns_dict(self):
        result = parse_sylk(_MINIMAL)
        assert isinstance(result, dict)

    def test_parse_sylk_ok_true(self):
        result = parse_sylk(_MINIMAL)
        assert result.get("ok") is True

    def test_parse_sylk_rows(self):
        result = parse_sylk(_MINIMAL)
        assert result.get("rows") == 2

    def test_parse_sylk_cols(self):
        result = parse_sylk(_MINIMAL)
        assert result.get("cols") == 2

    def test_parse_sylk_cell_count(self):
        result = parse_sylk(_MINIMAL)
        assert result.get("cell_count") == 4

    def test_parse_sylk_has_id_line(self):
        result = parse_sylk(_MINIMAL)
        assert "id_line" in result
        assert isinstance(result["id_line"], str)

    def test_probe_sylk_returns_dict(self):
        result = probe_sylk(_MINIMAL)
        assert isinstance(result, dict)

    def test_probe_sylk_exists(self):
        result = probe_sylk(_MINIMAL)
        assert result.get("exists") is True

    def test_probe_sylk_valid_header(self):
        result = probe_sylk(_MINIMAL)
        assert result.get("valid_header") is True

    def test_probe_sylk_has_id_line(self):
        result = probe_sylk(_MINIMAL)
        assert "id_line" in result

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "sylk"

    def test_get_capabilities_has_supported(self):
        caps = get_capabilities()
        assert isinstance(caps.get("supported"), list)
        assert len(caps["supported"]) > 0


class TestSylkDimensions:
    """get_row_count, get_cell_count, get_column_count, sylk_row_count."""

    def test_get_row_count_minimal(self):
        assert get_row_count(_MINIMAL) == 2

    def test_get_column_count_minimal(self):
        assert get_column_count(_MINIMAL) == 2

    def test_get_cell_count_minimal(self):
        assert get_cell_count(_MINIMAL) == 4

    def test_sylk_row_count_minimal(self):
        assert sylk_row_count(_MINIMAL) == 2

    def test_get_row_count_numeric(self):
        assert get_row_count(_NUMERIC) == 1

    def test_get_column_count_numeric(self):
        assert get_column_count(_NUMERIC) == 3

    def test_get_cell_count_numeric(self):
        assert get_cell_count(_NUMERIC) == 3


class TestSylkAnalytics:
    """sylk_numeric_cell_count, sylk_string_cell_count, sylk_empty_cell_count,
    sylk_total_sum, count_nonempty_cells, get_all_values."""

    def test_sylk_numeric_cell_count_minimal(self):
        # minimal-2x2: Name, Value (strings), Alpha (string), 42 (numeric)
        n = sylk_numeric_cell_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 1

    def test_sylk_string_cell_count_minimal(self):
        n = sylk_string_cell_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 3

    def test_sylk_empty_cell_count_minimal(self):
        n = sylk_empty_cell_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 0

    def test_sylk_total_sum_numeric(self):
        # numeric-row: values are 1, 2, 3 → sum=6
        total = sylk_total_sum(_NUMERIC)
        assert isinstance(total, (int, float))
        assert total == 6.0

    def test_count_nonempty_cells_minimal(self):
        n = count_nonempty_cells(_MINIMAL)
        assert isinstance(n, int)
        assert n == 4

    def test_get_all_values_minimal(self):
        vals = get_all_values(_MINIMAL)
        assert isinstance(vals, list)
        assert len(vals) == 4

    def test_get_all_values_contains_numeric(self):
        vals = get_all_values(_MINIMAL)
        assert 42 in vals or 42.0 in vals

    def test_get_all_values_contains_strings(self):
        vals = get_all_values(_MINIMAL)
        assert "Name" in vals

    def test_sylk_numeric_cell_count_numeric_row(self):
        # numeric-row: all 3 cells are numeric
        n = sylk_numeric_cell_count(_NUMERIC)
        assert n == 3

    def test_sylk_string_cell_count_numeric_row(self):
        n = sylk_string_cell_count(_NUMERIC)
        assert n == 0
