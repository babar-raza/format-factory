"""
test_r185_gnumeric_probe_deepening.py — Gnumeric probe + sheet metadata deepening tests

Sprint: PRODUCT-DEEPENING-RNEXT185-20260612-001
Gap closure: GAP-Gnumeric-FOSS-PROBE_GNUMER-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    probe_gnumeric,
    get_sheet_names,
    get_sheet_count,
    gnumeric_row_count_file,
    gnumeric_numeric_cell_count,
    gnumeric_string_cell_count,
    gnumeric_sheet_summary,
    get_column_count,
    row_count,
    load,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = _SAMPLES / "minimal-spreadsheet.gnumeric"
_MULTI = _SAMPLES / "multi-cell-basic.gnumeric"
_EMPTY = _SAMPLES / "empty-sheet.gnumeric"


class TestGnumericProbe:
    def test_probe_minimal_truthy(self):
        result = probe_gnumeric(str(_MINIMAL))
        assert result is not None  # probe returns True for valid file

    def test_probe_multi_truthy(self):
        result = probe_gnumeric(str(_MULTI))
        assert result is not None

    def test_sheet_names_minimal(self):
        names = get_sheet_names(str(_MINIMAL))
        assert isinstance(names, list)
        assert len(names) == 1

    def test_sheet_count_minimal(self):
        assert get_sheet_count(str(_MINIMAL)) == 1

    def test_sheet_count_multi(self):
        assert get_sheet_count(str(_MULTI)) >= 1

    def test_row_count_file_minimal(self):
        assert gnumeric_row_count_file(str(_MINIMAL)) >= 1


class TestGnumericSheetStats:
    def test_string_cell_count_minimal(self):
        model = load(str(_MINIMAL))
        count = gnumeric_string_cell_count(model, 0)
        assert count >= 1

    def test_numeric_cell_count_multi(self):
        model = load(str(_MULTI))
        count = gnumeric_numeric_cell_count(model, 0)
        assert count >= 1

    def test_sheet_summary_returns_dict(self):
        model = load(str(_MINIMAL))
        summary = gnumeric_sheet_summary(model, 0)
        assert isinstance(summary, dict)
        assert "row_count" in summary
        assert "col_count" in summary

    def test_sheet_summary_row_count_minimal(self):
        model = load(str(_MINIMAL))
        summary = gnumeric_sheet_summary(model, 0)
        assert summary["row_count"] >= 1

    def test_row_count_model_minimal(self):
        model = load(str(_MINIMAL))
        assert row_count(model, 0) >= 1

    def test_column_count_multi(self):
        model = load(str(_MULTI))
        assert get_column_count(model, 0) >= 1

    def test_row_count_file_multi_gt_minimal(self):
        r_min = gnumeric_row_count_file(str(_MINIMAL))
        r_multi = gnumeric_row_count_file(str(_MULTI))
        assert r_multi >= r_min
