"""Sprint 96 — ODS/QOI/XCF/CSV cycle 7: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_max_row_cell_count, ods_sheet_density
from src.python.qoi.qoi_parser import qoi_warm_pixel_count, qoi_cold_pixel_count
from src.python.xcf.xcf_parser import xcf_megapixel_count, xcf_layer_area_sum
from src.python.csv.csv_parser import csv_widest_field_length, csv_narrow_column_count

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
_CSV = _REPO / "samples" / "by-format" / "csv"


@pytest.fixture
def ods_sample():
    return next(_ODS.glob("*.ods"))


@pytest.fixture
def qoi_sample():
    return next(_QOI.glob("*.qoi"))


@pytest.fixture
def xcf_sample():
    return next(_XCF.glob("*.xcf"))


@pytest.fixture
def csv_sample():
    return _CSV / "minimal-2x2.csv"


# --- ODS ---

class TestOdsMaxRowCellCount:
    def test_returns_int(self, ods_sample):
        result = ods_max_row_cell_count(ods_sample)
        assert isinstance(result, int)

    def test_non_negative(self, ods_sample):
        assert ods_max_row_cell_count(ods_sample) >= 0


class TestOdsSheetDensity:
    def test_returns_float(self, ods_sample):
        result = ods_sheet_density(ods_sample)
        assert isinstance(result, (int, float))

    def test_non_negative(self, ods_sample):
        assert ods_sheet_density(ods_sample) >= 0.0


# --- QOI ---

class TestQoiWarmPixelCount:
    def test_returns_int(self, qoi_sample):
        result = qoi_warm_pixel_count(qoi_sample)
        assert isinstance(result, int)

    def test_non_negative(self, qoi_sample):
        assert qoi_warm_pixel_count(qoi_sample) >= 0


class TestQoiColdPixelCount:
    def test_returns_int(self, qoi_sample):
        result = qoi_cold_pixel_count(qoi_sample)
        assert isinstance(result, int)

    def test_non_negative(self, qoi_sample):
        assert qoi_cold_pixel_count(qoi_sample) >= 0

    def test_warm_plus_cold_lte_total(self, qoi_sample):
        warm = qoi_warm_pixel_count(qoi_sample)
        cold = qoi_cold_pixel_count(qoi_sample)
        from src.python.qoi.qoi_parser import parse_qoi_strict
        img = parse_qoi_strict(qoi_sample)
        assert warm + cold <= len(img.pixels)


# --- XCF ---

class TestXcfMegapixelCount:
    def test_returns_float(self, xcf_sample):
        result = xcf_megapixel_count(xcf_sample)
        assert isinstance(result, (int, float))

    def test_non_negative(self, xcf_sample):
        assert xcf_megapixel_count(xcf_sample) >= 0.0


class TestXcfLayerAreaSum:
    def test_returns_int(self, xcf_sample):
        result = xcf_layer_area_sum(xcf_sample)
        assert isinstance(result, int)

    def test_non_negative(self, xcf_sample):
        assert xcf_layer_area_sum(xcf_sample) >= 0


# --- CSV ---

class TestCsvWidestFieldLength:
    def test_returns_int(self, csv_sample):
        result = csv_widest_field_length(csv_sample)
        assert isinstance(result, int)

    def test_non_negative(self, csv_sample):
        assert csv_widest_field_length(csv_sample) >= 0


class TestCsvNarrowColumnCount:
    def test_returns_int(self, csv_sample):
        result = csv_narrow_column_count(csv_sample)
        assert isinstance(result, int)

    def test_non_negative(self, csv_sample):
        assert csv_narrow_column_count(csv_sample) >= 0
