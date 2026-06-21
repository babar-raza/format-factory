"""Sprint 110 — PPM/NDJSON/SYLK/DIF cycle 10: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_cold_pixel_ratio, ppm_red_green_diff
from src.python.ndjson.ndjson_codec import ndjson_array_field_count, ndjson_field_type_diversity
from src.python.sylk.sylk_parser import sylk_row_fill_rate, sylk_unique_cell_value_count
from src.python.dif.dif_parser import dif_min_row_width, dif_string_ratio

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))

_NDJSON_DATA = b'{"a":1,"b":"hello","c":[1,2]}\n{"a":2,"d":true}\n'


# --- PPM ---
def test_ppm_cold_pixel_ratio_importable():
    assert callable(ppm_cold_pixel_ratio)

def test_ppm_cold_pixel_ratio_returns_float():
    result = ppm_cold_pixel_ratio(_PPM)
    assert isinstance(result, float) and 0.0 <= result <= 1.0

def test_ppm_red_green_diff_importable():
    assert callable(ppm_red_green_diff)

def test_ppm_red_green_diff_returns_float():
    result = ppm_red_green_diff(_PPM)
    assert isinstance(result, float)


# --- NDJSON ---
def test_ndjson_array_field_count_importable():
    assert callable(ndjson_array_field_count)

def test_ndjson_array_field_count_returns_int():
    result = ndjson_array_field_count(_NDJSON_DATA)
    assert isinstance(result, int) and result >= 1

def test_ndjson_field_type_diversity_importable():
    assert callable(ndjson_field_type_diversity)

def test_ndjson_field_type_diversity_returns_int():
    result = ndjson_field_type_diversity(_NDJSON_DATA)
    assert isinstance(result, int) and result >= 2


# --- SYLK ---
def test_sylk_row_fill_rate_importable():
    assert callable(sylk_row_fill_rate)

def test_sylk_row_fill_rate_returns_float():
    result = sylk_row_fill_rate(_SYLK)
    assert isinstance(result, float) and result >= 0.0

def test_sylk_unique_cell_value_count_importable():
    assert callable(sylk_unique_cell_value_count)

def test_sylk_unique_cell_value_count_returns_int():
    result = sylk_unique_cell_value_count(_SYLK)
    assert isinstance(result, int) and result >= 0


# --- DIF ---
def test_dif_min_row_width_importable():
    assert callable(dif_min_row_width)

def test_dif_min_row_width_returns_int():
    result = dif_min_row_width(_DIF)
    assert isinstance(result, int) and result >= 0

def test_dif_string_ratio_importable():
    assert callable(dif_string_ratio)

def test_dif_string_ratio_returns_float():
    result = dif_string_ratio(_DIF)
    assert isinstance(result, float) and 0.0 <= result <= 1.0


# --- Integration ---
def test_all_eight_functions_callable():
    fns = [
        ppm_cold_pixel_ratio, ppm_red_green_diff,
        ndjson_array_field_count, ndjson_field_type_diversity,
        sylk_row_fill_rate, sylk_unique_cell_value_count,
        dif_min_row_width, dif_string_ratio,
    ]
    assert all(callable(f) for f in fns)
