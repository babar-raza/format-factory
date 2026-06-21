"""Sprint 120 — ODS/QOI/XCF/CSV cycle 13 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_numeric_value_mean, ods_cell_count_per_sheet
from src.python.qoi.qoi_parser import qoi_blue_mean_value, qoi_dark_ratio
from src.python.xcf.xcf_parser import xcf_height_squared, xcf_width_squared
from src.python.csv.csv_parser import csv_header_total_length, csv_numeric_value_sum

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsNumericValueMean:
    def test_returns_float(self):
        result = ods_numeric_value_mean(_ODS)
        assert isinstance(result, float)

    def test_invalid_sheet_index(self):
        assert ods_numeric_value_mean(_ODS, sheet_index=999) == 0.0


class TestOdsCellCountPerSheet:
    def test_returns_float(self):
        result = ods_cell_count_per_sheet(_ODS)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert ods_cell_count_per_sheet(_ODS) >= 0.0


class TestQoiBlueMeanValue:
    def test_returns_float(self):
        result = qoi_blue_mean_value(_QOI)
        assert isinstance(result, float)

    def test_range(self):
        result = qoi_blue_mean_value(_QOI)
        assert 0.0 <= result <= 255.0


class TestQoiDarkRatio:
    def test_returns_float(self):
        result = qoi_dark_ratio(_QOI)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = qoi_dark_ratio(_QOI)
        assert 0.0 <= result <= 1.0


class TestXcfHeightSquared:
    def test_returns_int(self):
        result = xcf_height_squared(_XCF)
        assert isinstance(result, int)

    def test_positive(self):
        assert xcf_height_squared(_XCF) > 0


class TestXcfWidthSquared:
    def test_returns_int(self):
        result = xcf_width_squared(_XCF)
        assert isinstance(result, int)

    def test_positive(self):
        assert xcf_width_squared(_XCF) > 0


class TestCsvHeaderTotalLength:
    def test_returns_int(self):
        result = csv_header_total_length(_CSV)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert csv_header_total_length(_CSV) >= 0


class TestCsvNumericValueSum:
    def test_returns_float(self):
        result = csv_numeric_value_sum(_CSV)
        assert isinstance(result, (int, float))
