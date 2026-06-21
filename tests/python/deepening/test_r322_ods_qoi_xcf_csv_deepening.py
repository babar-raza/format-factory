"""Sprint 92 — ODS/QOI/XCF/CSV cycle 6: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_merged_cell_ratio, ods_avg_string_length
from src.python.qoi.qoi_parser import qoi_dark_pixel_count, qoi_luminance_range
from src.python.xcf.xcf_parser import xcf_bytes_per_pixel, xcf_is_high_res
from src.python.csv.csv_parser import csv_max_column_name_length, csv_has_blank_headers

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
    return next(_CSV.glob("*.csv"))


# --- ODS ---
class TestOdsMergedCellRatio:
    def test_returns_float(self, ods_sample):
        result = ods_merged_cell_ratio(ods_sample)
        assert isinstance(result, float)

    def test_non_negative(self, ods_sample):
        assert ods_merged_cell_ratio(ods_sample) >= 0.0


class TestOdsAvgStringLength:
    def test_returns_float(self, ods_sample):
        result = ods_avg_string_length(ods_sample)
        assert isinstance(result, float)

    def test_non_negative(self, ods_sample):
        assert ods_avg_string_length(ods_sample) >= 0.0


# --- QOI ---
class TestQoiDarkPixelCount:
    def test_returns_int(self, qoi_sample):
        result = qoi_dark_pixel_count(qoi_sample)
        assert isinstance(result, int)

    def test_non_negative(self, qoi_sample):
        assert qoi_dark_pixel_count(qoi_sample) >= 0


class TestQoiLuminanceRange:
    def test_returns_float(self, qoi_sample):
        result = qoi_luminance_range(qoi_sample)
        assert isinstance(result, float)

    def test_non_negative(self, qoi_sample):
        assert qoi_luminance_range(qoi_sample) >= 0.0


# --- XCF ---
class TestXcfBytesPerPixel:
    def test_returns_float(self, xcf_sample):
        result = xcf_bytes_per_pixel(xcf_sample)
        assert isinstance(result, float)

    def test_positive(self, xcf_sample):
        assert xcf_bytes_per_pixel(xcf_sample) > 0.0


class TestXcfIsHighRes:
    def test_returns_bool(self, xcf_sample):
        result = xcf_is_high_res(xcf_sample)
        assert isinstance(result, bool)

    def test_deterministic(self, xcf_sample):
        assert xcf_is_high_res(xcf_sample) == xcf_is_high_res(xcf_sample)


# --- CSV ---
class TestCsvMaxColumnNameLength:
    def test_returns_int(self, csv_sample):
        result = csv_max_column_name_length(csv_sample)
        assert isinstance(result, int)

    def test_non_negative(self, csv_sample):
        assert csv_max_column_name_length(csv_sample) >= 0


class TestCsvHasBlankHeaders:
    def test_returns_bool(self, csv_sample):
        result = csv_has_blank_headers(csv_sample)
        assert isinstance(result, bool)

    def test_deterministic(self, csv_sample):
        assert csv_has_blank_headers(csv_sample) == csv_has_blank_headers(csv_sample)
