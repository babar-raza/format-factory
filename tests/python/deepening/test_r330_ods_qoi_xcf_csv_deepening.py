"""Sprint 100 — ODS/QOI/XCF/CSV cycle 8: 8 new analytics functions."""
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

def test_ods_string_cell_ratio_importable():
    from src.python.ods import ods_string_cell_ratio
    assert callable(ods_string_cell_ratio)


def test_ods_string_cell_ratio_returns_float(ods_sample):
    from src.python.ods import ods_string_cell_ratio
    result = ods_string_cell_ratio(ods_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_ods_widest_column_index_importable():
    from src.python.ods import ods_widest_column_index
    assert callable(ods_widest_column_index)


def test_ods_widest_column_index_returns_int(ods_sample):
    from src.python.ods import ods_widest_column_index
    result = ods_widest_column_index(ods_sample)
    assert isinstance(result, int)


# ── QOI ──

def test_qoi_red_channel_avg_importable():
    from src.python.qoi import qoi_red_channel_avg
    assert callable(qoi_red_channel_avg)


def test_qoi_red_channel_avg_returns_float(qoi_sample):
    from src.python.qoi import qoi_red_channel_avg
    result = qoi_red_channel_avg(qoi_sample)
    assert isinstance(result, float)
    assert result >= 0.0


def test_qoi_alpha_pixel_count_importable():
    from src.python.qoi import qoi_alpha_pixel_count
    assert callable(qoi_alpha_pixel_count)


def test_qoi_alpha_pixel_count_returns_int(qoi_sample):
    from src.python.qoi import qoi_alpha_pixel_count
    result = qoi_alpha_pixel_count(qoi_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── XCF ──

def test_xcf_diagonal_length_importable():
    from src.python.xcf import xcf_diagonal_length
    assert callable(xcf_diagonal_length)


def test_xcf_diagonal_length_returns_float(xcf_sample):
    from src.python.xcf import xcf_diagonal_length
    result = xcf_diagonal_length(xcf_sample)
    assert isinstance(result, float)
    assert result >= 0.0


def test_xcf_dimension_product_importable():
    from src.python.xcf import xcf_dimension_product
    assert callable(xcf_dimension_product)


def test_xcf_dimension_product_returns_int(xcf_sample):
    from src.python.xcf import xcf_dimension_product
    result = xcf_dimension_product(xcf_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── CSV ──

def test_csv_empty_field_count_importable():
    from src.python.ff_csv import csv_empty_field_count
    assert callable(csv_empty_field_count)


def test_csv_empty_field_count_returns_int(csv_sample):
    from src.python.ff_csv.csv_parser import csv_empty_field_count
    result = csv_empty_field_count(csv_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_csv_numeric_field_count_importable():
    from src.python.ff_csv import csv_numeric_field_count
    assert callable(csv_numeric_field_count)


def test_csv_numeric_field_count_returns_int(csv_sample):
    from src.python.ff_csv.csv_parser import csv_numeric_field_count
    result = csv_numeric_field_count(csv_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── Cross-format ──

def test_all_eight_functions_callable():
    """Verify all 8 Sprint 100 functions are importable."""
    from src.python.ods import ods_string_cell_ratio, ods_widest_column_index
    from src.python.qoi import qoi_red_channel_avg, qoi_alpha_pixel_count
    from src.python.xcf import xcf_diagonal_length, xcf_dimension_product
    from src.python.ff_csv.csv_parser import csv_empty_field_count, csv_numeric_field_count
    for fn in [
        ods_string_cell_ratio, ods_widest_column_index,
        qoi_red_channel_avg, qoi_alpha_pixel_count,
        xcf_diagonal_length, xcf_dimension_product,
        csv_empty_field_count, csv_numeric_field_count,
    ]:
        assert callable(fn)
