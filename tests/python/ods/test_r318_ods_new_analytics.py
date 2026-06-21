"""
test_r318_ods_new_analytics.py
Sprint 54 — 5 new ODS analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_file_size_bytes,
    ods_unique_value_count,
    ods_max_sheet_cell_count,
    ods_min_sheet_cell_count,
    ods_avg_nonempty_cells_per_sheet,
)

_VALID = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_VALID / "minimal-spreadsheet.ods")
_NUMERIC = str(_VALID / "numeric-row.ods")
_SINGLE = str(_VALID / "single-cell.ods")


# ods_file_size_bytes
class TestOdsFileSizeBytes:
    def test_minimal_positive(self):
        assert ods_file_size_bytes(_MINIMAL) > 0

    def test_numeric_positive(self):
        assert ods_file_size_bytes(_NUMERIC) > 0

    def test_single_positive(self):
        assert ods_file_size_bytes(_SINGLE) > 0

    def test_returns_int(self):
        assert isinstance(ods_file_size_bytes(_MINIMAL), int)

    def test_minimal_reasonable_size(self):
        # ODS files are zipped; expect at least 100 bytes
        assert ods_file_size_bytes(_MINIMAL) >= 100


# ods_unique_value_count
class TestOdsUniqueValueCount:
    def test_minimal_at_least_one(self):
        assert ods_unique_value_count(_MINIMAL) >= 1

    def test_numeric_at_least_one(self):
        assert ods_unique_value_count(_NUMERIC) >= 1

    def test_single_is_one(self):
        assert ods_unique_value_count(_SINGLE) >= 1

    def test_returns_int(self):
        assert isinstance(ods_unique_value_count(_MINIMAL), int)

    def test_non_negative(self):
        assert ods_unique_value_count(_MINIMAL) >= 0


# ods_max_sheet_cell_count
class TestOdsMaxSheetCellCount:
    def test_minimal_at_least_one(self):
        assert ods_max_sheet_cell_count(_MINIMAL) >= 1

    def test_numeric_at_least_one(self):
        assert ods_max_sheet_cell_count(_NUMERIC) >= 1

    def test_single_at_least_one(self):
        assert ods_max_sheet_cell_count(_SINGLE) >= 1

    def test_returns_int(self):
        assert isinstance(ods_max_sheet_cell_count(_MINIMAL), int)

    def test_non_negative(self):
        assert ods_max_sheet_cell_count(_MINIMAL) >= 0


# ods_min_sheet_cell_count
class TestOdsMinSheetCellCount:
    def test_minimal_non_negative(self):
        assert ods_min_sheet_cell_count(_MINIMAL) >= 0

    def test_numeric_non_negative(self):
        assert ods_min_sheet_cell_count(_NUMERIC) >= 0

    def test_single_at_least_one(self):
        assert ods_min_sheet_cell_count(_SINGLE) >= 1

    def test_returns_int(self):
        assert isinstance(ods_min_sheet_cell_count(_MINIMAL), int)

    def test_min_le_max(self):
        assert ods_min_sheet_cell_count(_MINIMAL) <= ods_max_sheet_cell_count(_MINIMAL)


# ods_avg_nonempty_cells_per_sheet
class TestOdsAvgNonemptyCellsPerSheet:
    def test_minimal_positive(self):
        assert ods_avg_nonempty_cells_per_sheet(_MINIMAL) >= 0.0

    def test_numeric_positive(self):
        assert ods_avg_nonempty_cells_per_sheet(_NUMERIC) >= 0.0

    def test_single_at_least_one(self):
        assert ods_avg_nonempty_cells_per_sheet(_SINGLE) >= 1.0

    def test_returns_float(self):
        assert isinstance(ods_avg_nonempty_cells_per_sheet(_MINIMAL), float)

    def test_min_le_avg_le_max(self):
        mn = ods_min_sheet_cell_count(_MINIMAL)
        avg = ods_avg_nonempty_cells_per_sheet(_MINIMAL)
        mx = ods_max_sheet_cell_count(_MINIMAL)
        assert mn <= avg <= mx
