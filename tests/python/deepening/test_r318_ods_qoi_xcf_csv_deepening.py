"""Sprint 88 — ODS/QOI/XCF/CSV cycle 5: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_string_column_count, ods_max_cell_text_length
from src.python.qoi.qoi_parser import qoi_color_count, qoi_avg_channel_value
from src.python.xcf.xcf_parser import xcf_pixel_per_layer_avg, xcf_canvas_aspect_ratio
from src.python.csv.csv_parser import csv_field_count_variance, csv_longest_field_value

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
class TestOdsStringColumnCount:
    def test_returns_int(self, ods_sample):
        result = ods_string_column_count(ods_sample)
        assert isinstance(result, int)

    def test_non_negative(self, ods_sample):
        assert ods_string_column_count(ods_sample) >= 0


class TestOdsMaxCellTextLength:
    def test_returns_int(self, ods_sample):
        result = ods_max_cell_text_length(ods_sample)
        assert isinstance(result, int)

    def test_non_negative(self, ods_sample):
        assert ods_max_cell_text_length(ods_sample) >= 0


# --- QOI ---
class TestQoiColorCount:
    def test_returns_int(self, qoi_sample):
        result = qoi_color_count(qoi_sample)
        assert isinstance(result, int)

    def test_positive(self, qoi_sample):
        assert qoi_color_count(qoi_sample) > 0


class TestQoiAvgChannelValue:
    def test_returns_float(self, qoi_sample):
        result = qoi_avg_channel_value(qoi_sample)
        assert isinstance(result, float)

    def test_in_range(self, qoi_sample):
        result = qoi_avg_channel_value(qoi_sample)
        assert 0.0 <= result <= 255.0


# --- XCF ---
class TestXcfPixelPerLayerAvg:
    def test_returns_float(self, xcf_sample):
        result = xcf_pixel_per_layer_avg(xcf_sample)
        assert isinstance(result, float)

    def test_positive(self, xcf_sample):
        assert xcf_pixel_per_layer_avg(xcf_sample) > 0.0


class TestXcfCanvasAspectRatio:
    def test_returns_float(self, xcf_sample):
        result = xcf_canvas_aspect_ratio(xcf_sample)
        assert isinstance(result, float)

    def test_positive(self, xcf_sample):
        assert xcf_canvas_aspect_ratio(xcf_sample) > 0.0


# --- CSV ---
class TestCsvFieldCountVariance:
    def test_returns_float(self, csv_sample):
        result = csv_field_count_variance(csv_sample)
        assert isinstance(result, float)

    def test_non_negative(self, csv_sample):
        assert csv_field_count_variance(csv_sample) >= 0.0


class TestCsvLongestFieldValue:
    def test_returns_int(self, csv_sample):
        result = csv_longest_field_value(csv_sample)
        assert isinstance(result, int)

    def test_non_negative(self, csv_sample):
        assert csv_longest_field_value(csv_sample) >= 0
