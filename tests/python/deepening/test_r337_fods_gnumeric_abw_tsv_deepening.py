"""Sprint 107 — FODS/GNUMERIC/ABW/TSV cycle 9: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods
from src.python.fods.neutral_model import fods_max_cell_length, fods_numeric_column_sum
from src.python.gnumeric.gnumeric_codec import gnumeric_column_data_rate, gnumeric_nonempty_ratio
from src.python.abw.abw_codec import abw_char_per_paragraph, abw_paragraph_text_variance
from src.python.tsv.tsv_parser import tsv_column_count_avg, tsv_field_length_variance

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = next((_REPO / "samples" / "by-format" / "tsv").glob("*.tsv"))


# --- FODS ---
def test_fods_max_cell_length_importable():
    assert callable(fods_max_cell_length)

def test_fods_max_cell_length_returns_int():
    wb = parse_fods(_FODS)
    result = fods_max_cell_length(wb)
    assert isinstance(result, int) and result >= 0

def test_fods_numeric_column_sum_importable():
    assert callable(fods_numeric_column_sum)

def test_fods_numeric_column_sum_returns_float():
    wb = parse_fods(_FODS)
    result = fods_numeric_column_sum(wb)
    assert isinstance(result, float)


# --- GNUMERIC ---
def test_gnumeric_column_data_rate_importable():
    assert callable(gnumeric_column_data_rate)

def test_gnumeric_column_data_rate_returns_float():
    result = gnumeric_column_data_rate(_GNUMERIC)
    assert isinstance(result, float) and result >= 0.0

def test_gnumeric_nonempty_ratio_importable():
    assert callable(gnumeric_nonempty_ratio)

def test_gnumeric_nonempty_ratio_returns_float():
    result = gnumeric_nonempty_ratio(_GNUMERIC)
    assert isinstance(result, float) and result >= 0.0


# --- ABW ---
def test_abw_char_per_paragraph_importable():
    assert callable(abw_char_per_paragraph)

def test_abw_char_per_paragraph_returns_float():
    result = abw_char_per_paragraph(_ABW)
    assert isinstance(result, float) and result >= 0.0

def test_abw_paragraph_text_variance_importable():
    assert callable(abw_paragraph_text_variance)

def test_abw_paragraph_text_variance_returns_float():
    result = abw_paragraph_text_variance(_ABW)
    assert isinstance(result, float) and result >= 0.0


# --- TSV ---
def test_tsv_column_count_avg_importable():
    assert callable(tsv_column_count_avg)

def test_tsv_column_count_avg_returns_float():
    result = tsv_column_count_avg(_TSV)
    assert isinstance(result, float) and result >= 0.0

def test_tsv_field_length_variance_importable():
    assert callable(tsv_field_length_variance)

def test_tsv_field_length_variance_returns_float():
    result = tsv_field_length_variance(_TSV)
    assert isinstance(result, float) and result >= 0.0


# --- Integration ---
def test_all_eight_functions_callable():
    fns = [
        fods_max_cell_length, fods_numeric_column_sum,
        gnumeric_column_data_rate, gnumeric_nonempty_ratio,
        abw_char_per_paragraph, abw_paragraph_text_variance,
        tsv_column_count_avg, tsv_field_length_variance,
    ]
    assert all(callable(f) for f in fns)
