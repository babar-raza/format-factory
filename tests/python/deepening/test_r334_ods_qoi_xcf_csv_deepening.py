"""Sprint 104 — ODS/QOI/XCF/CSV cycle 9: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

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


# ── ODS ──

def test_ods_numeric_cell_ratio_importable():
    from src.python.ods import ods_numeric_cell_ratio
    assert callable(ods_numeric_cell_ratio)

def test_ods_numeric_cell_ratio_returns_float(ods_sample):
    from src.python.ods import ods_numeric_cell_ratio
    result = ods_numeric_cell_ratio(ods_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0

def test_ods_column_fill_rate_importable():
    from src.python.ods import ods_column_fill_rate
    assert callable(ods_column_fill_rate)

def test_ods_column_fill_rate_returns_float(ods_sample):
    from src.python.ods import ods_column_fill_rate
    result = ods_column_fill_rate(ods_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── QOI ──

def test_qoi_green_channel_avg_importable():
    from src.python.qoi import qoi_green_channel_avg
    assert callable(qoi_green_channel_avg)

def test_qoi_green_channel_avg_returns_float(qoi_sample):
    from src.python.qoi import qoi_green_channel_avg
    result = qoi_green_channel_avg(qoi_sample)
    assert isinstance(result, float)
    assert result >= 0.0

def test_qoi_blue_channel_avg_importable():
    from src.python.qoi import qoi_blue_channel_avg
    assert callable(qoi_blue_channel_avg)

def test_qoi_blue_channel_avg_returns_float(qoi_sample):
    from src.python.qoi import qoi_blue_channel_avg
    result = qoi_blue_channel_avg(qoi_sample)
    assert isinstance(result, float)
    assert result >= 0.0


# ── XCF ──

def test_xcf_is_square_canvas_importable():
    from src.python.xcf import xcf_is_square_canvas
    assert callable(xcf_is_square_canvas)

def test_xcf_is_square_canvas_returns_bool(xcf_sample):
    from src.python.xcf import xcf_is_square_canvas
    result = xcf_is_square_canvas(xcf_sample)
    assert isinstance(result, bool)

def test_xcf_total_layer_area_importable():
    from src.python.xcf import xcf_total_layer_area
    assert callable(xcf_total_layer_area)

def test_xcf_total_layer_area_returns_int(xcf_sample):
    from src.python.xcf import xcf_total_layer_area
    result = xcf_total_layer_area(xcf_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── CSV ──

def test_csv_row_width_avg_importable():
    from src.python.csv import csv_row_width_avg
    assert callable(csv_row_width_avg)

def test_csv_row_width_avg_returns_float(csv_sample):
    from src.python.csv.csv_parser import csv_row_width_avg
    result = csv_row_width_avg(csv_sample)
    assert isinstance(result, float)
    assert result >= 0.0

def test_csv_distinct_header_count_importable():
    from src.python.csv import csv_distinct_header_count
    assert callable(csv_distinct_header_count)

def test_csv_distinct_header_count_returns_int(csv_sample):
    from src.python.csv.csv_parser import csv_distinct_header_count
    result = csv_distinct_header_count(csv_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── Cross-format ──

def test_all_eight_functions_callable():
    from src.python.ods import ods_numeric_cell_ratio, ods_column_fill_rate
    from src.python.qoi import qoi_green_channel_avg, qoi_blue_channel_avg
    from src.python.xcf import xcf_is_square_canvas, xcf_total_layer_area
    from src.python.csv.csv_parser import csv_row_width_avg, csv_distinct_header_count
    for fn in [
        ods_numeric_cell_ratio, ods_column_fill_rate,
        qoi_green_channel_avg, qoi_blue_channel_avg,
        xcf_is_square_canvas, xcf_total_layer_area,
        csv_row_width_avg, csv_distinct_header_count,
    ]:
        assert callable(fn)
