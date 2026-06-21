"""
DIF FOSS gap closure tests.

Closes:
  GAP-DIF-FOSS-DIF_NONEMPTY-001  — dif_nonempty_cell_ratio
  GAP-DIF-FOSS-DIF_AVG_NUME-001  — dif_avg_numeric_value
  GAP-DIF-FOSS-DIF_ROW_LENG-001  — dif_row_length_variance
  GAP-DIF-FOSS-DIF_EMPTY_CO-001  — dif_empty_column_count
  GAP-DIF-FOSS-DIF_LONGEST_-001  — dif_longest_row_index
  GAP-DIF-FOSS-DIF_TOTAL_ST-001  — dif_total_string_length
  GAP-DIF-FOSS-DIF_COLUMN_D-001  — dif_column_density
  GAP-DIF-FOSS-DIF_TOTAL_CE-001  — dif_total_cell_length

Run from repo root:
    python -m pytest tests/python/dif/test_dif_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from dif.dif_parser import (
    dif_nonempty_cell_ratio,
    dif_avg_numeric_value,
    dif_row_length_variance,
    dif_empty_column_count,
    dif_longest_row_index,
    dif_total_string_length,
    dif_column_density,
    dif_total_cell_length,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "dif" / "valid"
SINGLE = SAMPLES / "single-cell.dif"
TWO_X_TWO = SAMPLES / "minimal-2x2.dif"
NUMERIC = SAMPLES / "numeric-row.dif"


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_NONEMPTY-001 — dif_nonempty_cell_ratio
# ---------------------------------------------------------------------------

class TestDifNonemptyCellRatio:
    def test_single_cell_fully_populated(self):
        assert dif_nonempty_cell_ratio(SINGLE) == pytest.approx(1.0, abs=0.01)

    def test_two_x_two_fully_populated(self):
        assert dif_nonempty_cell_ratio(TWO_X_TWO) == pytest.approx(1.0, abs=0.01)

    def test_returns_float(self):
        assert isinstance(dif_nonempty_cell_ratio(SINGLE), float)

    def test_bounded_zero_to_one(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            r = dif_nonempty_cell_ratio(p)
            assert 0.0 <= r <= 1.0


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_AVG_NUME-001 — dif_avg_numeric_value
# ---------------------------------------------------------------------------

class TestDifAvgNumericValue:
    def test_single_cell_value(self):
        assert dif_avg_numeric_value(SINGLE) == pytest.approx(42.0, abs=0.01)

    def test_two_x_two_value(self):
        assert dif_avg_numeric_value(TWO_X_TWO) == pytest.approx(70.5, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(dif_avg_numeric_value(SINGLE), (int, float))

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert dif_avg_numeric_value(p) >= 0


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_ROW_LENG-001 — dif_row_length_variance
# ---------------------------------------------------------------------------

class TestDifRowLengthVariance:
    def test_single_cell_zero_variance(self):
        assert dif_row_length_variance(SINGLE) == pytest.approx(0.0, abs=0.01)

    def test_two_x_two_zero_variance(self):
        # all rows same length
        assert dif_row_length_variance(TWO_X_TWO) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(dif_row_length_variance(SINGLE), (int, float))

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert dif_row_length_variance(p) >= 0


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_EMPTY_CO-001 — dif_empty_column_count
# ---------------------------------------------------------------------------

class TestDifEmptyColumnCount:
    def test_single_cell_no_empty_columns(self):
        assert dif_empty_column_count(SINGLE) == 0

    def test_two_x_two_no_empty_columns(self):
        assert dif_empty_column_count(TWO_X_TWO) == 0

    def test_returns_int(self):
        assert isinstance(dif_empty_column_count(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert dif_empty_column_count(p) >= 0


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_LONGEST_-001 — dif_longest_row_index
# ---------------------------------------------------------------------------

class TestDifLongestRowIndex:
    def test_single_cell_index_zero(self):
        assert dif_longest_row_index(SINGLE) == 0

    def test_two_x_two_index_zero(self):
        assert dif_longest_row_index(TWO_X_TWO) == 0

    def test_returns_int(self):
        assert isinstance(dif_longest_row_index(SINGLE), int)


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_TOTAL_ST-001 — dif_total_string_length
# ---------------------------------------------------------------------------

class TestDifTotalStringLength:
    def test_single_cell_positive(self):
        assert dif_total_string_length(SINGLE) > 0

    def test_two_x_two_larger_than_single(self):
        assert dif_total_string_length(TWO_X_TWO) > dif_total_string_length(SINGLE)

    def test_returns_int(self):
        assert isinstance(dif_total_string_length(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert dif_total_string_length(p) >= 0


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_COLUMN_D-001 — dif_column_density
# ---------------------------------------------------------------------------

class TestDifColumnDensity:
    def test_single_cell_full_density(self):
        assert dif_column_density(SINGLE) == pytest.approx(1.0, abs=0.01)

    def test_two_x_two_full_density(self):
        assert dif_column_density(TWO_X_TWO) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(dif_column_density(SINGLE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            r = dif_column_density(p)
            assert 0.0 <= r <= 1.0


# ---------------------------------------------------------------------------
# GAP-DIF-FOSS-DIF_TOTAL_CE-001 — dif_total_cell_length
# ---------------------------------------------------------------------------

class TestDifTotalCellLength:
    def test_single_cell_positive(self):
        assert dif_total_cell_length(SINGLE) > 0

    def test_two_x_two_larger_than_single(self):
        assert dif_total_cell_length(TWO_X_TWO) > dif_total_cell_length(SINGLE)

    def test_returns_int(self):
        assert isinstance(dif_total_cell_length(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert dif_total_cell_length(p) >= 0
