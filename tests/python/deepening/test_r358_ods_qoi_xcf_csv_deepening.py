"""Sprint 128 — ODS/QOI/XCF/CSV cycle 15: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_cell_type_variety, ods_row_density
from src.python.qoi.qoi_parser import qoi_pixel_brightness_mean, qoi_alpha_ratio
from src.python.xcf.xcf_parser import xcf_canvas_half_perimeter, xcf_layer_count_ratio
from src.python.csv.csv_parser import csv_numeric_field_mean, csv_row_length_min

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsCellTypeVariety:
    def test_returns_int(self):
        result = ods_cell_type_variety(_ODS)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert ods_cell_type_variety(_ODS) >= 0


class TestOdsRowDensity:
    def test_returns_float(self):
        result = ods_row_density(_ODS)
        assert isinstance(result, float)

    def test_in_range(self):
        r = ods_row_density(_ODS)
        assert 0.0 <= r <= 1.0


class TestQoiPixelBrightnessMean:
    def test_returns_float(self):
        result = qoi_pixel_brightness_mean(_QOI)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert qoi_pixel_brightness_mean(_QOI) >= 0.0


class TestQoiAlphaRatio:
    def test_returns_float(self):
        result = qoi_alpha_ratio(_QOI)
        assert isinstance(result, float)

    def test_in_range(self):
        r = qoi_alpha_ratio(_QOI)
        assert 0.0 <= r <= 1.0


class TestXcfCanvasHalfPerimeter:
    def test_returns_int(self):
        result = xcf_canvas_half_perimeter(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert xcf_canvas_half_perimeter(_XCF) >= 0


class TestXcfLayerCountRatio:
    def test_returns_float(self):
        result = xcf_layer_count_ratio(_XCF)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert xcf_layer_count_ratio(_XCF) >= 0.0


class TestCsvNumericFieldMean:
    def test_returns_float(self):
        result = csv_numeric_field_mean(_CSV)
        assert isinstance(result, float)


class TestCsvRowLengthMin:
    def test_returns_int(self):
        result = csv_row_length_min(_CSV)
        assert isinstance(result, int)

    def test_positive(self):
        assert csv_row_length_min(_CSV) > 0
