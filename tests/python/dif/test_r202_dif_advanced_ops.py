"""
tests/python/dif/test_r202_dif_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT16-001
TASK-001 (part B): DIF advanced operations.

Covers: parse_dif, parse_dif_strict, probe_dif, get_capabilities, get_row_count,
get_column_count, dif_vectors_count, total_cell_count, count_nonempty_cells,
get_all_values, sum_column, average_column, dif_numeric_range, dif_string_cell_count,
dif_empty_row_count, dif_string_value_list, dif_vector_density.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    parse_dif, parse_dif_strict, probe_dif, get_capabilities, get_row_count,
    get_column_count, dif_vectors_count, total_cell_count, count_nonempty_cells,
    get_all_values, sum_column, average_column,
)
from dif.dif_stats import (
    dif_numeric_range, dif_string_cell_count, dif_empty_row_count,
    dif_string_value_list, dif_vector_density,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.dif")
_NUMERIC = str(_SAMPLES / "numeric-row.dif")


class TestDifParseAndProbe:
    """parse_dif, parse_dif_strict, probe_dif, get_capabilities."""

    def test_parse_dif_returns_dict(self):
        result = parse_dif(_MINIMAL)
        assert isinstance(result, dict)

    def test_parse_dif_ok_true(self):
        result = parse_dif(_MINIMAL)
        assert result.get("ok") is True

    def test_parse_dif_has_title(self):
        result = parse_dif(_MINIMAL)
        assert "title" in result

    def test_parse_dif_has_rows(self):
        result = parse_dif(_MINIMAL)
        assert isinstance(result.get("rows"), list)

    def test_parse_dif_strict_returns_object(self):
        # parse_dif_strict may return DifDocument or dict
        result = parse_dif_strict(_MINIMAL)
        assert result is not None

    def test_probe_dif_dict(self):
        result = probe_dif(_MINIMAL)
        assert isinstance(result, dict)
        assert result.get("exists") is True

    def test_probe_dif_valid_header(self):
        result = probe_dif(_MINIMAL)
        assert result.get("valid_header") is True

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "dif"


class TestDifStructureOps:
    """get_row_count, get_column_count, dif_vectors_count, total_cell_count, count_nonempty_cells."""

    def test_get_row_count_int(self):
        n = get_row_count(_MINIMAL)
        assert isinstance(n, int)
        assert n >= 1

    def test_get_column_count_int(self):
        n = get_column_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 2

    def test_dif_vectors_count_int(self):
        n = dif_vectors_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 2

    def test_total_cell_count_int(self):
        n = total_cell_count(_MINIMAL)
        assert isinstance(n, int)
        assert n > 0

    def test_count_nonempty_cells_int(self):
        n = count_nonempty_cells(_MINIMAL)
        assert isinstance(n, int)
        assert n > 0

    def test_get_all_values_list(self):
        vals = get_all_values(_MINIMAL)
        assert isinstance(vals, list)
        assert len(vals) > 0

    def test_numeric_row_column_count(self):
        n = get_column_count(_NUMERIC)
        assert n == 3


class TestDifAnalytics:
    """sum_column, average_column, dif_numeric_range, dif_string_cell_count, dif_empty_row_count."""

    def test_sum_column_numeric_row(self):
        s = sum_column(_NUMERIC, 0)
        assert isinstance(s, (int, float))

    def test_average_column_numeric_row(self):
        avg = average_column(_NUMERIC, 0)
        assert isinstance(avg, (int, float))

    def test_dif_numeric_range_dict(self):
        doc = parse_dif(_NUMERIC)
        result = dif_numeric_range(doc)
        assert isinstance(result, dict)
        assert "min_value" in result
        assert "max_value" in result

    def test_dif_numeric_range_values(self):
        doc = parse_dif(_NUMERIC)
        result = dif_numeric_range(doc)
        assert result["min_value"] == 1.0
        assert result["max_value"] == 3.0

    def test_dif_string_cell_count_int(self):
        doc = parse_dif(_NUMERIC)
        n = dif_string_cell_count(doc)
        assert isinstance(n, int)
        assert n == 0  # numeric-row has no strings

    def test_dif_empty_row_count_int(self):
        doc = parse_dif(_NUMERIC)
        n = dif_empty_row_count(doc)
        assert isinstance(n, int)
        assert n == 0

    def test_dif_string_value_list_list(self):
        doc = parse_dif(_NUMERIC)
        result = dif_string_value_list(doc)
        assert isinstance(result, list)

    def test_dif_numeric_count_is_three(self):
        doc = parse_dif(_NUMERIC)
        result = dif_numeric_range(doc)
        assert result.get("numeric_count") == 3
