"""Sprint 124 — ODS/QOI/XCF/CSV cycle 14 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_cell_text_avg_length, ods_cell_type_count
from src.python.qoi.qoi_parser import qoi_green_mean_value, qoi_light_ratio
from src.python.xcf.xcf_parser import xcf_width_height_sum, xcf_canvas_diagonal
from src.python.csv.csv_parser import csv_field_length_variance, csv_row_width_variance

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsCellTextAvgLength:
    def test_returns_float(self):
        assert isinstance(ods_cell_text_avg_length(_ODS), float)

    def test_non_negative(self):
        assert ods_cell_text_avg_length(_ODS) >= 0.0


class TestOdsCellTypeCount:
    def test_returns_int(self):
        assert isinstance(ods_cell_type_count(_ODS), int)

    def test_non_negative(self):
        assert ods_cell_type_count(_ODS) >= 0


class TestQoiGreenMeanValue:
    def test_returns_float(self):
        assert isinstance(qoi_green_mean_value(_QOI), float)

    def test_non_negative(self):
        assert qoi_green_mean_value(_QOI) >= 0.0


class TestQoiLightRatio:
    def test_returns_float(self):
        assert isinstance(qoi_light_ratio(_QOI), float)

    def test_range(self):
        assert 0.0 <= qoi_light_ratio(_QOI) <= 1.0


class TestXcfWidthHeightSum:
    def test_returns_int(self):
        assert isinstance(xcf_width_height_sum(_XCF), int)

    def test_positive(self):
        assert xcf_width_height_sum(_XCF) > 0


class TestXcfCanvasDiagonal:
    def test_returns_float(self):
        assert isinstance(xcf_canvas_diagonal(_XCF), float)

    def test_positive(self):
        assert xcf_canvas_diagonal(_XCF) > 0.0


class TestCsvFieldLengthVariance:
    def test_returns_float(self):
        assert isinstance(csv_field_length_variance(_CSV), float)

    def test_non_negative(self):
        assert csv_field_length_variance(_CSV) >= 0.0


class TestCsvRowWidthVariance:
    def test_returns_float(self):
        assert isinstance(csv_row_width_variance(_CSV), float)

    def test_non_negative(self):
        assert csv_row_width_variance(_CSV) >= 0.0
