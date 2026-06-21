"""Sprint 128 deepening – DIF is_single_tuple/string_to_numeric_ratio, CSV numeric_to_string_ratio/avg_row_cell_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_is_single_tuple, dif_string_to_numeric_ratio
from src.python.csv.csv_parser import csv_numeric_to_string_ratio, csv_avg_row_cell_count

DIF = _REPO / "samples" / "by-format" / "dif" / "valid"
CSV = _REPO / "samples" / "by-format" / "csv"


# --- dif_is_single_tuple ---

class TestDifIsSingleTuple:
    def test_minimal_false(self):
        assert dif_is_single_tuple(DIF / "minimal-2x2.dif") is False

    def test_numeric_true(self):
        assert dif_is_single_tuple(DIF / "numeric-row.dif") is True

    def test_single_true(self):
        assert dif_is_single_tuple(DIF / "single-cell.dif") is True

    def test_returns_bool(self):
        assert isinstance(dif_is_single_tuple(DIF / "minimal-2x2.dif"), bool)

    def test_single_cell_is_single(self):
        assert dif_is_single_tuple(DIF / "single-cell.dif") is True


# --- dif_string_to_numeric_ratio ---

class TestDifStringToNumericRatio:
    def test_minimal(self):
        assert abs(dif_string_to_numeric_ratio(DIF / "minimal-2x2.dif") - 3.0) < 0.01

    def test_numeric_zero(self):
        assert dif_string_to_numeric_ratio(DIF / "numeric-row.dif") == 0.0

    def test_single_zero(self):
        assert dif_string_to_numeric_ratio(DIF / "single-cell.dif") == 0.0

    def test_returns_float(self):
        assert isinstance(dif_string_to_numeric_ratio(DIF / "minimal-2x2.dif"), float)

    def test_non_negative(self):
        assert dif_string_to_numeric_ratio(DIF / "minimal-2x2.dif") >= 0


# --- csv_numeric_to_string_ratio ---

class TestCsvNumericToStringRatio:
    def test_minimal(self):
        assert abs(csv_numeric_to_string_ratio(CSV / "minimal-2x2.csv") - 1.0) < 0.01

    def test_quoted(self):
        assert abs(csv_numeric_to_string_ratio(CSV / "quoted-fields.csv") - 0.5) < 0.01

    def test_single_zero(self):
        assert csv_numeric_to_string_ratio(CSV / "single-cell.csv") == 0.0

    def test_returns_float(self):
        assert isinstance(csv_numeric_to_string_ratio(CSV / "minimal-2x2.csv"), float)

    def test_non_negative(self):
        assert csv_numeric_to_string_ratio(CSV / "minimal-2x2.csv") >= 0


# --- csv_avg_row_cell_count ---

class TestCsvAvgRowCellCount:
    def test_minimal(self):
        assert abs(csv_avg_row_cell_count(CSV / "minimal-2x2.csv") - 2.0) < 0.01

    def test_quoted(self):
        assert abs(csv_avg_row_cell_count(CSV / "quoted-fields.csv") - 3.0) < 0.01

    def test_single(self):
        assert abs(csv_avg_row_cell_count(CSV / "single-cell.csv") - 1.0) < 0.01

    def test_returns_float(self):
        assert isinstance(csv_avg_row_cell_count(CSV / "minimal-2x2.csv"), float)

    def test_positive(self):
        assert csv_avg_row_cell_count(CSV / "minimal-2x2.csv") > 0
