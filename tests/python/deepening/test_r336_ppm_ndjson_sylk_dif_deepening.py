"""Sprint 106 — PPM/NDJSON/SYLK/DIF cycle 9: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_channel_sum, ppm_pixel_brightness_avg
from src.python.ndjson.ndjson_codec import ndjson_record_size_max, ndjson_nested_object_count
from src.python.sylk.sylk_parser import sylk_max_column_sum, sylk_empty_row_count
from src.python.dif.dif_parser import dif_avg_row_width, dif_header_count

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))

_NDJSON_DATA = b'{"a":1,"b":"hello"}\n{"a":2,"c":true}\n{"a":3,"b":"","d":null}\n'


# --- PPM ---
def test_ppm_channel_sum_importable():
    assert callable(ppm_channel_sum)

def test_ppm_channel_sum_returns_int():
    result = ppm_channel_sum(_PPM)
    assert isinstance(result, int) and result >= 0

def test_ppm_pixel_brightness_avg_importable():
    assert callable(ppm_pixel_brightness_avg)

def test_ppm_pixel_brightness_avg_returns_float():
    result = ppm_pixel_brightness_avg(_PPM)
    assert isinstance(result, float) and result >= 0.0


# --- NDJSON ---
def test_ndjson_record_size_max_importable():
    assert callable(ndjson_record_size_max)

def test_ndjson_record_size_max_returns_int():
    result = ndjson_record_size_max(_NDJSON_DATA)
    assert isinstance(result, int) and result >= 2

def test_ndjson_nested_object_count_importable():
    assert callable(ndjson_nested_object_count)

def test_ndjson_nested_object_count_returns_int():
    result = ndjson_nested_object_count(_NDJSON_DATA)
    assert isinstance(result, int) and result >= 0


# --- SYLK ---
def test_sylk_max_column_sum_importable():
    assert callable(sylk_max_column_sum)

def test_sylk_max_column_sum_returns_float():
    result = sylk_max_column_sum(_SYLK)
    assert isinstance(result, (int, float))

def test_sylk_empty_row_count_importable():
    assert callable(sylk_empty_row_count)

def test_sylk_empty_row_count_returns_int():
    result = sylk_empty_row_count(_SYLK)
    assert isinstance(result, int) and result >= 0


# --- DIF ---
def test_dif_avg_row_width_importable():
    assert callable(dif_avg_row_width)

def test_dif_avg_row_width_returns_float():
    result = dif_avg_row_width(_DIF)
    assert isinstance(result, float) and result >= 0.0

def test_dif_header_count_importable():
    assert callable(dif_header_count)

def test_dif_header_count_returns_int():
    result = dif_header_count(_DIF)
    assert isinstance(result, int) and result >= 0


# --- Integration ---
def test_all_eight_functions_callable():
    fns = [
        ppm_channel_sum, ppm_pixel_brightness_avg,
        ndjson_record_size_max, ndjson_nested_object_count,
        sylk_max_column_sum, sylk_empty_row_count,
        dif_avg_row_width, dif_header_count,
    ]
    assert all(callable(f) for f in fns)
