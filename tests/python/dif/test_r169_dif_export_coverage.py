"""
test_r169_dif_export_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT10-001
Added: 2026-06-11

Tests for DIF export and accessor functions: probe_dif, dif_to_csv,
export_to_html, get_row_count, get_column_count, get_cell_value,
get_row_values, get_column_values, get_title, sum_column, total_cell_count,
count_nonempty_cells.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    probe_dif,
    parse_dif,
    dif_to_csv,
    export_to_html,
    get_row_count,
    get_column_count,
    get_cell_value,
    get_row_values,
    get_column_values,
    get_title,
    sum_column,
    total_cell_count,
    count_nonempty_cells,
    get_all_values,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = _SAMPLES / "minimal-2x2.dif"
_NUMERIC = _SAMPLES / "numeric-row.dif"


# ── probe_dif ─────────────────────────────────────────────────────────────

class TestProbeDif:

    def test_returns_dict(self):
        result = probe_dif(_MINIMAL)
        assert isinstance(result, dict)

    def test_exists_true(self):
        result = probe_dif(_MINIMAL)
        assert result.get("exists") is True

    def test_has_valid_header(self):
        result = probe_dif(_MINIMAL)
        assert result.get("valid_header") is True

    def test_has_title(self):
        result = probe_dif(_MINIMAL)
        assert "title" in result

    def test_nonexistent_file(self, tmp_path):
        result = probe_dif(tmp_path / "no_such.dif")
        assert result.get("exists") is False


# ── dif_to_csv ────────────────────────────────────────────────────────────

class TestDifToCsv:

    def test_returns_string(self):
        result = dif_to_csv(_MINIMAL)
        assert isinstance(result, str)

    def test_nonempty(self):
        result = dif_to_csv(_MINIMAL)
        assert len(result.strip()) > 0

    def test_from_numeric_file(self):
        result = dif_to_csv(_NUMERIC)
        assert isinstance(result, str)


# ── export_to_html ────────────────────────────────────────────────────────

class TestExportToHtml:

    def test_returns_string(self):
        result = export_to_html(_MINIMAL)
        assert isinstance(result, str)

    def test_has_table_tag(self):
        result = export_to_html(_MINIMAL)
        assert "<table>" in result

    def test_has_tr_td_tags(self):
        result = export_to_html(_MINIMAL)
        assert "<tr>" in result and "<td>" in result


# ── get_row_count / get_column_count ──────────────────────────────────────

class TestRowColumnCounts:

    def test_get_row_count_int(self):
        assert isinstance(get_row_count(_MINIMAL), int)

    def test_get_row_count_positive(self):
        assert get_row_count(_MINIMAL) >= 1

    def test_get_column_count_int(self):
        assert isinstance(get_column_count(_MINIMAL), int)

    def test_get_column_count_positive(self):
        assert get_column_count(_MINIMAL) >= 1


# ── get_cell_value ────────────────────────────────────────────────────────

class TestGetCellValue:

    def test_returns_value(self):
        result = get_cell_value(_MINIMAL, 0, 0)
        assert result is not None

    def test_numeric_row(self):
        result = get_cell_value(_NUMERIC, 0, 0)
        assert result is not None


# ── get_row_values / get_column_values ────────────────────────────────────

class TestGetRowAndColumnValues:

    def test_get_row_values_list(self):
        result = get_row_values(_MINIMAL, 0)
        assert isinstance(result, list)

    def test_get_row_values_nonempty(self):
        result = get_row_values(_MINIMAL, 0)
        assert len(result) >= 1

    def test_get_column_values_list(self):
        result = get_column_values(_MINIMAL, 0)
        assert isinstance(result, list)


# ── get_title ─────────────────────────────────────────────────────────────

class TestGetTitle:

    def test_returns_string(self):
        result = get_title(_MINIMAL)
        assert isinstance(result, str)

    def test_title_nonempty(self):
        result = get_title(_MINIMAL)
        assert len(result) > 0


# ── sum_column ────────────────────────────────────────────────────────────

class TestSumColumn:

    def test_returns_float(self):
        result = sum_column(_MINIMAL, 0)
        assert isinstance(result, float)

    def test_numeric_sum(self):
        # numeric-row.dif has numeric values in col 1
        result = sum_column(_NUMERIC, 1)
        assert isinstance(result, float)


# ── total_cell_count / count_nonempty_cells ───────────────────────────────

class TestCellCounts:

    def test_total_cell_count_int(self):
        assert isinstance(total_cell_count(_MINIMAL), int)

    def test_total_cell_count_positive(self):
        assert total_cell_count(_MINIMAL) > 0

    def test_count_nonempty_cells_int(self):
        assert isinstance(count_nonempty_cells(_MINIMAL), int)

    def test_count_nonempty_le_total(self):
        total = total_cell_count(_MINIMAL)
        nonempty = count_nonempty_cells(_MINIMAL)
        assert nonempty <= total


# ── get_all_values ────────────────────────────────────────────────────────

class TestGetAllValues:

    def test_returns_list(self):
        result = get_all_values(_MINIMAL)
        assert isinstance(result, list)

    def test_nonempty(self):
        result = get_all_values(_MINIMAL)
        assert len(result) > 0
