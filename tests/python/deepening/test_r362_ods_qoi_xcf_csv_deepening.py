"""Sprint 132 — ODS/QOI/XCF/CSV cycle 16: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_numeric_cell_variance, ods_cell_value_mean
from src.python.qoi.qoi_parser import qoi_red_mean_value, qoi_channel_range_sum
from src.python.xcf.xcf_parser import xcf_area_to_layer_ratio, xcf_min_side_length
from src.python.csv.csv_parser import csv_header_field_count, csv_field_text_mean_length

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsNumericCellVariance:
    def test_returns_float(self):
        result = ods_numeric_cell_variance(_ODS)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert ods_numeric_cell_variance(_ODS) >= 0.0


class TestOdsCellValueMean:
    def test_returns_float(self):
        result = ods_cell_value_mean(_ODS)
        assert isinstance(result, float)


class TestQoiRedMeanValue:
    def test_returns_float(self):
        result = qoi_red_mean_value(_QOI)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert qoi_red_mean_value(_QOI) >= 0.0


class TestQoiChannelRangeSum:
    def test_returns_int(self):
        result = qoi_channel_range_sum(_QOI)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert qoi_channel_range_sum(_QOI) >= 0


class TestXcfAreaToLayerRatio:
    def test_returns_float(self):
        result = xcf_area_to_layer_ratio(_XCF)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert xcf_area_to_layer_ratio(_XCF) >= 0.0


class TestXcfMinSideLength:
    def test_returns_int(self):
        result = xcf_min_side_length(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert xcf_min_side_length(_XCF) >= 0


class TestCsvHeaderFieldCount:
    def test_returns_int(self):
        result = csv_header_field_count(_CSV)
        assert isinstance(result, int)

    def test_positive(self):
        assert csv_header_field_count(_CSV) > 0


class TestCsvFieldTextMeanLength:
    def test_returns_float(self):
        result = csv_field_text_mean_length(_CSV)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert csv_field_text_mean_length(_CSV) >= 0.0
