"""Sprint 136 — ODS/QOI/XCF/CSV cycle 17 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


# ---------- ODS ----------
class TestOdsValueTypeCount:
    def test_returns_int(self):
        from src.python.ods import ods_value_type_count
        assert isinstance(ods_value_type_count(_ODS), int)

    def test_non_negative(self):
        from src.python.ods import ods_value_type_count
        assert ods_value_type_count(_ODS) >= 0


class TestOdsNonemptyCellPercentage:
    def test_returns_float(self):
        from src.python.ods import ods_nonempty_cell_percentage
        assert isinstance(ods_nonempty_cell_percentage(_ODS), (int, float))

    def test_bounded(self):
        from src.python.ods import ods_nonempty_cell_percentage
        result = ods_nonempty_cell_percentage(_ODS)
        assert 0.0 <= result <= 100.0


# ---------- QOI ----------
class TestQoiOpaquePixelCount:
    def test_returns_int(self):
        from src.python.qoi import qoi_opaque_pixel_count
        assert isinstance(qoi_opaque_pixel_count(_QOI), int)

    def test_non_negative(self):
        from src.python.qoi import qoi_opaque_pixel_count
        assert qoi_opaque_pixel_count(_QOI) >= 0


class TestQoiPixelBrightnessSum:
    def test_returns_int(self):
        from src.python.qoi import qoi_pixel_brightness_sum
        assert isinstance(qoi_pixel_brightness_sum(_QOI), int)

    def test_non_negative(self):
        from src.python.qoi import qoi_pixel_brightness_sum
        assert qoi_pixel_brightness_sum(_QOI) >= 0


# ---------- XCF ----------
class TestXcfPerimeterLength:
    def test_returns_int(self):
        from src.python.xcf import xcf_perimeter_length
        assert isinstance(xcf_perimeter_length(_XCF), int)

    def test_positive(self):
        from src.python.xcf import xcf_perimeter_length
        assert xcf_perimeter_length(_XCF) > 0


class TestXcfMaxSideLength:
    def test_returns_int(self):
        from src.python.xcf import xcf_max_side_length
        assert isinstance(xcf_max_side_length(_XCF), int)

    def test_positive(self):
        from src.python.xcf import xcf_max_side_length
        assert xcf_max_side_length(_XCF) > 0


# ---------- CSV ----------
class TestCsvFieldValueVariance:
    def test_returns_float(self):
        from src.python.ff_csv.csv_parser import csv_field_value_variance
        assert isinstance(csv_field_value_variance(_CSV), (int, float))

    def test_non_negative(self):
        from src.python.ff_csv.csv_parser import csv_field_value_variance
        assert csv_field_value_variance(_CSV) >= 0.0


class TestCsvRowTextTotal:
    def test_returns_int(self):
        from src.python.ff_csv.csv_parser import csv_row_text_total
        assert isinstance(csv_row_text_total(_CSV), int)

    def test_non_negative(self):
        from src.python.ff_csv.csv_parser import csv_row_text_total
        assert csv_row_text_total(_CSV) >= 0
