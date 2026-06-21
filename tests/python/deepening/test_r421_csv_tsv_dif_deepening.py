"""Tests for 6 new analytics: CSV/TSV/DIF deepening sprint R421."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_row_count_squared,
    csv_field_count_plus_row_count,
    csv_row_count,
    csv_total_field_count,
)

from src.python.tsv.tsv_parser import (
    tsv_row_count_squared,
    tsv_field_count_plus_row_count,
    tsv_row_count,
    tsv_total_field_count,
)

from src.python.dif.dif_parser import (
    dif_row_count_squared,
    dif_cell_count_plus_row_count,
    dif_row_count,
    dif_total_cell_count,
)

_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"


class TestCsvRowCountSquared:
    def test_returns_int(self):
        assert isinstance(csv_row_count_squared(_CSV), int)

    def test_matches_formula(self):
        rc = csv_row_count(_CSV)
        assert csv_row_count_squared(_CSV) == rc * rc

    def test_positive(self):
        assert csv_row_count_squared(_CSV) >= 1


class TestCsvFieldCountPlusRowCount:
    def test_returns_int(self):
        assert isinstance(csv_field_count_plus_row_count(_CSV), int)

    def test_matches_sum(self):
        assert csv_field_count_plus_row_count(_CSV) == csv_total_field_count(_CSV) + csv_row_count(_CSV)

    def test_positive(self):
        assert csv_field_count_plus_row_count(_CSV) >= 1


class TestTsvRowCountSquared:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_squared(_TSV), int)

    def test_matches_formula(self):
        rc = tsv_row_count(_TSV)
        assert tsv_row_count_squared(_TSV) == rc * rc

    def test_positive(self):
        assert tsv_row_count_squared(_TSV) >= 1


class TestTsvFieldCountPlusRowCount:
    def test_returns_int(self):
        assert isinstance(tsv_field_count_plus_row_count(_TSV), int)

    def test_matches_sum(self):
        assert tsv_field_count_plus_row_count(_TSV) == tsv_total_field_count(_TSV) + tsv_row_count(_TSV)

    def test_positive(self):
        assert tsv_field_count_plus_row_count(_TSV) >= 1


class TestDifRowCountSquared:
    def test_returns_int(self):
        assert isinstance(dif_row_count_squared(_DIF), int)

    def test_matches_formula(self):
        rc = dif_row_count(_DIF)
        assert dif_row_count_squared(_DIF) == rc * rc

    def test_positive(self):
        assert dif_row_count_squared(_DIF) >= 1


class TestDifCellCountPlusRowCount:
    def test_returns_int(self):
        assert isinstance(dif_cell_count_plus_row_count(_DIF), int)

    def test_matches_sum(self):
        assert dif_cell_count_plus_row_count(_DIF) == dif_total_cell_count(_DIF) + dif_row_count(_DIF)

    def test_positive(self):
        assert dif_cell_count_plus_row_count(_DIF) >= 1
