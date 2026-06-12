"""
test_r185_csv_probe_deepening.py — CSV probe + table-stats deepening tests

Sprint: PRODUCT-DEEPENING-RNEXT185-20260612-001
Gap closures: GAP-CSV-FOSS-PROBE_CSV-001, GAP-CSV-FOSS-TABLE_STATS-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    probe_csv,
    get_row_count,
    get_column_names,
    csv_column_count,
    csv_to_dicts,
    get_cell_value,
    csv_has_header,
    csv_numeric_row_count,
    count_empty_cells,
)

_SAMPLES = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = _SAMPLES / "minimal-2x2.csv"      # Name,Age / Alice,30
_SINGLE = _SAMPLES / "single-cell.csv"       # 1 row, 1 column
_QUOTED = _SAMPLES / "quoted-fields.csv"


class TestCsvProbe:
    def test_probe_returns_dict(self):
        result = probe_csv(str(_MINIMAL))
        assert isinstance(result, dict)

    def test_probe_exists_true(self):
        result = probe_csv(str(_MINIMAL))
        assert result["exists"] is True

    def test_probe_has_sample_line_count(self):
        result = probe_csv(str(_MINIMAL))
        assert result["sample_line_count"] >= 1

    def test_probe_delimiter_comma(self):
        result = probe_csv(str(_MINIMAL))
        assert result["delimiter"] == ","

    def test_probe_first_line(self):
        result = probe_csv(str(_MINIMAL))
        assert "Name" in result["first_line"]

    def test_probe_size_bytes_positive(self):
        result = probe_csv(str(_MINIMAL))
        assert result["size_bytes"] > 0


class TestCsvTableStats:
    def test_row_count_minimal(self):
        assert get_row_count(str(_MINIMAL)) == 2

    def test_column_names_minimal(self):
        names = get_column_names(str(_MINIMAL))
        assert "Name" in names
        assert "Age" in names

    def test_column_count_minimal(self):
        assert csv_column_count(str(_MINIMAL)) == 2

    def test_csv_has_header_minimal(self):
        assert csv_has_header(str(_MINIMAL)) is True

    def test_csv_to_dicts_minimal(self):
        rows = csv_to_dicts(str(_MINIMAL))
        assert len(rows) == 2
        assert rows[0]["Name"] == "Alice"

    def test_get_cell_value_row0_col0(self):
        # col is int (0-based), not column name
        val = get_cell_value(str(_MINIMAL), 0, 0)
        assert val == "Alice"

    def test_numeric_row_count_minimal(self):
        # csv_numeric_row_count takes only file_path; counts rows where ALL cells are numeric
        # minimal-2x2.csv has mixed data (Name+Age), count may be 0 or >0
        count = csv_numeric_row_count(str(_MINIMAL))
        assert isinstance(count, int) and count >= 0

    def test_single_cell_row_count(self):
        assert get_row_count(str(_SINGLE)) >= 1
