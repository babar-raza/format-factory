"""Sprint 108 — ODS/QOI/XCF/CSV cycle 10: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_avg_cell_text_length, ods_has_single_sheet
from src.python.qoi.qoi_parser import qoi_warm_pixel_ratio, qoi_pixel_brightness_range
from src.python.xcf.xcf_parser import xcf_has_single_layer, xcf_aspect_ratio_string
from src.python.csv.csv_parser import csv_longest_field_length, csv_header_uniqueness_ratio

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


# --- ODS ---
def test_ods_avg_cell_text_length_importable():
    assert callable(ods_avg_cell_text_length)

def test_ods_avg_cell_text_length_returns_float():
    result = ods_avg_cell_text_length(_ODS)
    assert isinstance(result, float) and result >= 0.0

def test_ods_has_single_sheet_importable():
    assert callable(ods_has_single_sheet)

def test_ods_has_single_sheet_returns_bool():
    result = ods_has_single_sheet(_ODS)
    assert isinstance(result, bool)


# --- QOI ---
def test_qoi_warm_pixel_ratio_importable():
    assert callable(qoi_warm_pixel_ratio)

def test_qoi_warm_pixel_ratio_returns_float():
    result = qoi_warm_pixel_ratio(_QOI)
    assert isinstance(result, float) and 0.0 <= result <= 1.0

def test_qoi_pixel_brightness_range_importable():
    assert callable(qoi_pixel_brightness_range)

def test_qoi_pixel_brightness_range_returns_int():
    result = qoi_pixel_brightness_range(_QOI)
    assert isinstance(result, int) and result >= 0


# --- XCF ---
def test_xcf_has_single_layer_importable():
    assert callable(xcf_has_single_layer)

def test_xcf_has_single_layer_returns_bool():
    result = xcf_has_single_layer(_XCF)
    assert isinstance(result, bool)

def test_xcf_aspect_ratio_string_importable():
    assert callable(xcf_aspect_ratio_string)

def test_xcf_aspect_ratio_string_returns_str():
    result = xcf_aspect_ratio_string(_XCF)
    assert isinstance(result, str) and ":" in result


# --- CSV ---
def test_csv_longest_field_length_importable():
    assert callable(csv_longest_field_length)

def test_csv_longest_field_length_returns_int():
    result = csv_longest_field_length(_CSV)
    assert isinstance(result, int) and result >= 0

def test_csv_header_uniqueness_ratio_importable():
    assert callable(csv_header_uniqueness_ratio)

def test_csv_header_uniqueness_ratio_returns_float():
    result = csv_header_uniqueness_ratio(_CSV)
    assert isinstance(result, float) and 0.0 <= result <= 1.0


# --- Integration ---
def test_all_eight_functions_callable():
    fns = [
        ods_avg_cell_text_length, ods_has_single_sheet,
        qoi_warm_pixel_ratio, qoi_pixel_brightness_range,
        xcf_has_single_layer, xcf_aspect_ratio_string,
        csv_longest_field_length, csv_header_uniqueness_ratio,
    ]
    assert all(callable(f) for f in fns)
