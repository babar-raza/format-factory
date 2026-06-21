"""Sprint 116 — ODS/QOI/XCF/CSV cycle 12 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_row_cell_sum, ods_max_string_length
from src.python.qoi.qoi_parser import qoi_red_channel_mean, qoi_pixel_uniformity
from src.python.xcf.xcf_parser import xcf_layer_count_squared, xcf_total_canvas_pixels
from src.python.csv.csv_parser import csv_empty_row_ratio, csv_max_row_width

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsRowCellSum:
    def test_returns_int(self):
        result = ods_row_cell_sum(_ODS)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert ods_row_cell_sum(_ODS) >= 0

    def test_invalid_sheet_index(self):
        assert ods_row_cell_sum(_ODS, sheet_index=999) == 0


class TestOdsMaxStringLength:
    def test_returns_int(self):
        result = ods_max_string_length(_ODS)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert ods_max_string_length(_ODS) >= 0


class TestQoiRedChannelMean:
    def test_returns_float(self):
        result = qoi_red_channel_mean(_QOI)
        assert isinstance(result, float)

    def test_range(self):
        result = qoi_red_channel_mean(_QOI)
        assert 0.0 <= result <= 255.0


class TestQoiPixelUniformity:
    def test_returns_float(self):
        result = qoi_pixel_uniformity(_QOI)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = qoi_pixel_uniformity(_QOI)
        assert 0.0 <= result <= 1.0


class TestXcfLayerCountSquared:
    def test_returns_int(self):
        result = xcf_layer_count_squared(_XCF)
        assert isinstance(result, int)

    def test_positive(self):
        assert xcf_layer_count_squared(_XCF) > 0


class TestXcfTotalCanvasPixels:
    def test_returns_int(self):
        result = xcf_total_canvas_pixels(_XCF)
        assert isinstance(result, int)

    def test_positive(self):
        assert xcf_total_canvas_pixels(_XCF) > 0


class TestCsvEmptyRowRatio:
    def test_returns_float(self):
        result = csv_empty_row_ratio(_CSV)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = csv_empty_row_ratio(_CSV)
        assert 0.0 <= result <= 1.0


class TestCsvMaxRowWidth:
    def test_returns_int(self):
        result = csv_max_row_width(_CSV)
        assert isinstance(result, int)

    def test_positive(self):
        assert csv_max_row_width(_CSV) > 0
