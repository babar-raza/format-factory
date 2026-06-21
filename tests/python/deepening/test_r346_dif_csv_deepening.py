"""Sprint 136 — DIF numeric_ratio/is_all_numeric, CSV numeric_ratio/is_all_numeric."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.dif.dif_parser import dif_numeric_ratio, dif_is_all_numeric
from src.python.csv.csv_parser import csv_numeric_ratio, csv_is_all_numeric

D1 = str(_REPO / "samples/by-format/dif/valid/minimal-2x2.dif")
D2 = str(_REPO / "samples/by-format/dif/valid/numeric-row.dif")
D3 = str(_REPO / "samples/by-format/dif/valid/single-cell.dif")
C1 = str(_REPO / "samples/by-format/csv/minimal-2x2.csv")
C2 = str(_REPO / "samples/by-format/csv/quoted-fields.csv")
C3 = str(_REPO / "samples/by-format/csv/single-cell.csv")

class TestDifNumericRatio:
    def test_minimal(self):
        assert dif_numeric_ratio(D1) == 0.25
    def test_numeric_row(self):
        assert dif_numeric_ratio(D2) == 1.0
    def test_single(self):
        assert dif_numeric_ratio(D3) == 1.0
    def test_return_type(self):
        assert isinstance(dif_numeric_ratio(D1), float)
    def test_bounded(self):
        assert 0.0 <= dif_numeric_ratio(D1) <= 1.0

class TestDifIsAllNumeric:
    def test_minimal(self):
        assert dif_is_all_numeric(D1) is False
    def test_numeric_row(self):
        assert dif_is_all_numeric(D2) is True
    def test_single(self):
        assert dif_is_all_numeric(D3) is True
    def test_return_type(self):
        assert isinstance(dif_is_all_numeric(D1), bool)
    def test_consistency(self):
        assert dif_is_all_numeric(D2) == (dif_numeric_ratio(D2) == 1.0)

class TestCsvNumericRatio:
    def test_minimal(self):
        assert csv_numeric_ratio(C1) == 0.5
    def test_quoted(self):
        assert abs(csv_numeric_ratio(C2) - 0.3333) < 0.01
    def test_single(self):
        assert csv_numeric_ratio(C3) == 1.0
    def test_return_type(self):
        assert isinstance(csv_numeric_ratio(C1), float)
    def test_bounded(self):
        assert 0.0 <= csv_numeric_ratio(C1) <= 1.0

class TestCsvIsAllNumeric:
    def test_minimal(self):
        assert csv_is_all_numeric(C1) is False
    def test_quoted(self):
        assert csv_is_all_numeric(C2) is False
    def test_single(self):
        assert csv_is_all_numeric(C3) is True
    def test_return_type(self):
        assert isinstance(csv_is_all_numeric(C1), bool)
    def test_consistency(self):
        assert csv_is_all_numeric(C3) == (csv_numeric_ratio(C3) == 1.0)
