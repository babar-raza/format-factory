"""Sprint 112 — ODS/QOI/XCF/CSV cycle 11: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_cell_text_density, ods_sheet_cell_variance
from src.python.qoi.qoi_parser import qoi_channel_skew, qoi_green_dominance_ratio
from src.python.xcf.xcf_parser import xcf_min_layer_area, xcf_layer_width_sum
from src.python.csv.csv_parser import csv_row_length_range, csv_blank_field_ratio

_ODS = next((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_QOI = next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_CSV = next((_REPO / "samples" / "by-format" / "csv").glob("minimal-2x2.csv"))


# --- ODS ---
def test_ods_cell_text_density_importable():
    assert callable(ods_cell_text_density)

def test_ods_cell_text_density_returns_float():
    result = ods_cell_text_density(_ODS)
    assert isinstance(result, (int, float)) and result >= 0

def test_ods_sheet_cell_variance_importable():
    assert callable(ods_sheet_cell_variance)

def test_ods_sheet_cell_variance_returns_float():
    result = ods_sheet_cell_variance(_ODS)
    assert isinstance(result, (int, float)) and result >= 0


# --- QOI ---
def test_qoi_channel_skew_importable():
    assert callable(qoi_channel_skew)

def test_qoi_channel_skew_returns_float():
    result = qoi_channel_skew(_QOI)
    assert isinstance(result, float)

def test_qoi_green_dominance_ratio_importable():
    assert callable(qoi_green_dominance_ratio)

def test_qoi_green_dominance_ratio_returns_float():
    result = qoi_green_dominance_ratio(_QOI)
    assert isinstance(result, float) and 0.0 <= result <= 1.0


# --- XCF ---
def test_xcf_min_layer_area_importable():
    assert callable(xcf_min_layer_area)

def test_xcf_min_layer_area_returns_int():
    result = xcf_min_layer_area(_XCF)
    assert isinstance(result, int) and result >= 0

def test_xcf_layer_width_sum_importable():
    assert callable(xcf_layer_width_sum)

def test_xcf_layer_width_sum_returns_int():
    result = xcf_layer_width_sum(_XCF)
    assert isinstance(result, int) and result >= 0


# --- CSV ---
def test_csv_row_length_range_importable():
    assert callable(csv_row_length_range)

def test_csv_row_length_range_returns_int():
    result = csv_row_length_range(_CSV)
    assert isinstance(result, int) and result >= 0

def test_csv_blank_field_ratio_importable():
    assert callable(csv_blank_field_ratio)

def test_csv_blank_field_ratio_returns_float():
    result = csv_blank_field_ratio(_CSV)
    assert isinstance(result, float) and 0.0 <= result <= 1.0
