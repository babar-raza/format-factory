"""Sprint 86 — PPM/NDJSON/SYLK/DIF cycle 4 product deepening tests.

Functions under test:
  PPM:    ppm_min_channel_avg, ppm_max_pixel_brightness
  NDJSON: ndjson_nested_count, ndjson_min_record_fields
  SYLK:   sylk_value_length_sum, sylk_avg_row_density
  DIF:    dif_value_type_variance, dif_total_cell_length
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# PPM -------------------------------------------------------------------------
from src.python.ppm.ppm_parser import ppm_min_channel_avg, ppm_max_pixel_brightness

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"

def test_ppm_min_channel_avg_type():
    samples = list(_PPM.glob("*.ppm"))
    assert samples
    r = ppm_min_channel_avg(samples[0])
    assert isinstance(r, float)

def test_ppm_min_channel_avg_non_negative():
    for s in _PPM.glob("*.ppm"):
        assert ppm_min_channel_avg(s) >= 0.0

def test_ppm_max_pixel_brightness_type():
    samples = list(_PPM.glob("*.ppm"))
    assert samples
    r = ppm_max_pixel_brightness(samples[0])
    assert isinstance(r, float)

def test_ppm_max_pixel_brightness_non_negative():
    for s in _PPM.glob("*.ppm"):
        assert ppm_max_pixel_brightness(s) >= 0.0

# NDJSON ----------------------------------------------------------------------
from src.python.ndjson.ndjson_codec import ndjson_nested_count, ndjson_min_record_fields

_NDJSON_DATA = b'{"name":"alice","meta":{"role":"admin"}}\n{"name":"bob","meta":{"role":"user"}}\n'

def test_ndjson_nested_count_type():
    r = ndjson_nested_count(_NDJSON_DATA)
    assert isinstance(r, int)

def test_ndjson_nested_count_positive():
    assert ndjson_nested_count(_NDJSON_DATA) > 0

def test_ndjson_min_record_fields_type():
    r = ndjson_min_record_fields(_NDJSON_DATA)
    assert isinstance(r, int)

def test_ndjson_min_record_fields_positive():
    assert ndjson_min_record_fields(_NDJSON_DATA) > 0

# SYLK ------------------------------------------------------------------------
from src.python.sylk.sylk_parser import sylk_value_length_sum, sylk_avg_row_density

_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"

def test_sylk_value_length_sum_type():
    samples = list(_SYLK.glob("*.slk"))
    assert samples
    r = sylk_value_length_sum(samples[0])
    assert isinstance(r, int)

def test_sylk_value_length_sum_non_negative():
    for s in _SYLK.glob("*.slk"):
        assert sylk_value_length_sum(s) >= 0

def test_sylk_avg_row_density_type():
    samples = list(_SYLK.glob("*.slk"))
    assert samples
    r = sylk_avg_row_density(samples[0])
    assert isinstance(r, float)

def test_sylk_avg_row_density_non_negative():
    for s in _SYLK.glob("*.slk"):
        assert sylk_avg_row_density(s) >= 0.0

# DIF -------------------------------------------------------------------------
from src.python.dif.dif_parser import dif_value_type_variance, dif_total_cell_length

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"

def test_dif_value_type_variance_type():
    samples = list(_DIF.glob("*.dif"))
    assert samples
    r = dif_value_type_variance(samples[0])
    assert isinstance(r, float)

def test_dif_value_type_variance_non_negative():
    for s in _DIF.glob("*.dif"):
        assert dif_value_type_variance(s) >= 0.0

def test_dif_total_cell_length_type():
    samples = list(_DIF.glob("*.dif"))
    assert samples
    r = dif_total_cell_length(samples[0])
    assert isinstance(r, int)

def test_dif_total_cell_length_non_negative():
    for s in _DIF.glob("*.dif"):
        assert dif_total_cell_length(s) >= 0
