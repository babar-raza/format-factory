"""Sprint 82 — PPM/NDJSON/SYLK/DIF cycle 3 product deepening tests.

Functions under test:
  PPM:    ppm_green_ratio, ppm_pixel_brightness_range
  NDJSON: ndjson_string_density, ndjson_avg_list_length
  SYLK:   sylk_string_value_count, sylk_has_empty_cells
  DIF:    dif_string_value_count, dif_max_numeric_length
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# PPM -------------------------------------------------------------------------
from src.python.ppm.ppm_parser import ppm_green_ratio, ppm_pixel_brightness_range

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"

def test_ppm_green_ratio_type():
    samples = list(_PPM.glob("*.ppm"))
    assert samples, "no PPM samples"
    r = ppm_green_ratio(samples[0])
    assert isinstance(r, float)

def test_ppm_green_ratio_range():
    for s in _PPM.glob("*.ppm"):
        r = ppm_green_ratio(s)
        assert 0.0 <= r <= 1.0, f"{s.name}: {r}"

def test_ppm_pixel_brightness_range_type():
    samples = list(_PPM.glob("*.ppm"))
    assert samples
    r = ppm_pixel_brightness_range(samples[0])
    assert isinstance(r, float)

def test_ppm_pixel_brightness_range_non_negative():
    for s in _PPM.glob("*.ppm"):
        assert ppm_pixel_brightness_range(s) >= 0.0

# NDJSON ----------------------------------------------------------------------
from src.python.ndjson.ndjson_codec import ndjson_string_density, ndjson_avg_list_length

_NDJSON_DATA = b'{"name":"alice","age":30,"tags":["a","b"]}\n{"name":"bob","age":25,"tags":["c"]}\n'

def test_ndjson_string_density_type():
    r = ndjson_string_density(_NDJSON_DATA)
    assert isinstance(r, float)

def test_ndjson_string_density_range():
    r = ndjson_string_density(_NDJSON_DATA)
    assert 0.0 <= r <= 1.0

def test_ndjson_avg_list_length_type():
    r = ndjson_avg_list_length(_NDJSON_DATA)
    assert isinstance(r, float)

def test_ndjson_avg_list_length_positive():
    r = ndjson_avg_list_length(_NDJSON_DATA)
    assert r > 0.0, "should have list fields with positive avg length"

# SYLK ------------------------------------------------------------------------
from src.python.sylk.sylk_parser import sylk_string_value_count, sylk_has_empty_cells

_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"

def test_sylk_string_value_count_type():
    samples = list(_SYLK.glob("*.slk"))
    assert samples
    r = sylk_string_value_count(samples[0])
    assert isinstance(r, int)

def test_sylk_string_value_count_non_negative():
    for s in _SYLK.glob("*.slk"):
        assert sylk_string_value_count(s) >= 0

def test_sylk_has_empty_cells_type():
    samples = list(_SYLK.glob("*.slk"))
    assert samples
    r = sylk_has_empty_cells(samples[0])
    assert isinstance(r, bool)

# DIF -------------------------------------------------------------------------
from src.python.dif.dif_parser import dif_string_value_count, dif_max_numeric_length

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"

def test_dif_string_value_count_type():
    samples = list(_DIF.glob("*.dif"))
    assert samples
    r = dif_string_value_count(samples[0])
    assert isinstance(r, int)

def test_dif_string_value_count_non_negative():
    for s in _DIF.glob("*.dif"):
        assert dif_string_value_count(s) >= 0

def test_dif_max_numeric_length_type():
    samples = list(_DIF.glob("*.dif"))
    assert samples
    r = dif_max_numeric_length(samples[0])
    assert isinstance(r, int)

def test_dif_max_numeric_length_non_negative():
    for s in _DIF.glob("*.dif"):
        assert dif_max_numeric_length(s) >= 0
