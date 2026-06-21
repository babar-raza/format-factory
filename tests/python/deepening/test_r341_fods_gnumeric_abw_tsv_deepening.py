"""Sprint 111 — FODS/GNUMERIC/ABW/TSV cycle 10: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods
from src.python.fods.neutral_model import fods_cell_count_variance, fods_row_width_variance
from src.python.gnumeric.gnumeric_codec import gnumeric_cell_text_sum, gnumeric_row_fill_variance
from src.python.abw.abw_codec import abw_has_single_paragraph, abw_digit_ratio
from src.python.tsv.tsv_parser import tsv_has_header_row, tsv_row_field_variance

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = next((_REPO / "samples" / "by-format" / "tsv").glob("*.tsv"))


# --- FODS ---
def test_fods_cell_count_variance_importable():
    assert callable(fods_cell_count_variance)

def test_fods_cell_count_variance_returns_float():
    wb = parse_fods(_FODS)
    result = fods_cell_count_variance(wb)
    assert isinstance(result, (int, float)) and result >= 0

def test_fods_row_width_variance_importable():
    assert callable(fods_row_width_variance)

def test_fods_row_width_variance_returns_float():
    wb = parse_fods(_FODS)
    result = fods_row_width_variance(wb)
    assert isinstance(result, (int, float)) and result >= 0


# --- GNUMERIC ---
def test_gnumeric_cell_text_sum_importable():
    assert callable(gnumeric_cell_text_sum)

def test_gnumeric_cell_text_sum_returns_int():
    result = gnumeric_cell_text_sum(_GNUMERIC)
    assert isinstance(result, int) and result >= 0

def test_gnumeric_row_fill_variance_importable():
    assert callable(gnumeric_row_fill_variance)

def test_gnumeric_row_fill_variance_returns_float():
    result = gnumeric_row_fill_variance(_GNUMERIC)
    assert isinstance(result, (int, float)) and result >= 0


# --- ABW ---
def test_abw_has_single_paragraph_importable():
    assert callable(abw_has_single_paragraph)

def test_abw_has_single_paragraph_returns_bool():
    result = abw_has_single_paragraph(_ABW)
    assert isinstance(result, bool)

def test_abw_digit_ratio_importable():
    assert callable(abw_digit_ratio)

def test_abw_digit_ratio_returns_float():
    result = abw_digit_ratio(_ABW)
    assert isinstance(result, float) and 0.0 <= result <= 1.0


# --- TSV ---
def test_tsv_has_header_row_importable():
    assert callable(tsv_has_header_row)

def test_tsv_has_header_row_returns_bool():
    result = tsv_has_header_row(_TSV)
    assert isinstance(result, bool)

def test_tsv_row_field_variance_importable():
    assert callable(tsv_row_field_variance)

def test_tsv_row_field_variance_returns_float():
    result = tsv_row_field_variance(_TSV)
    assert isinstance(result, (int, float)) and result >= 0
