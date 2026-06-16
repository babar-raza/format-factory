"""Sprint 85 — PBM/PGM/FODP/FODT cycle 4 product deepening tests.

Functions under test:
  PBM:  pbm_total_black_in_border, pbm_center_black_ratio
  PGM:  pgm_median_brightness, pgm_pixel_value_range
  FODP: fodp_shortest_slide_index, fodp_shape_count_variance
  FODT: fodt_total_char_count, fodt_heading_to_para_ratio
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# PBM -------------------------------------------------------------------------
from src.python.pbm.pbm_parser import pbm_total_black_in_border, pbm_center_black_ratio

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"

def test_pbm_total_black_in_border_type():
    samples = list(_PBM.glob("*.pbm"))
    assert samples
    r = pbm_total_black_in_border(samples[0])
    assert isinstance(r, int)

def test_pbm_total_black_in_border_non_negative():
    for s in _PBM.glob("*.pbm"):
        assert pbm_total_black_in_border(s) >= 0

def test_pbm_center_black_ratio_type():
    samples = list(_PBM.glob("*.pbm"))
    assert samples
    r = pbm_center_black_ratio(samples[0])
    assert isinstance(r, float)

def test_pbm_center_black_ratio_range():
    for s in _PBM.glob("*.pbm"):
        r = pbm_center_black_ratio(s)
        assert 0.0 <= r <= 1.0, f"{s.name}: {r}"

# PGM -------------------------------------------------------------------------
from src.python.pgm.pgm_parser import pgm_median_brightness, pgm_pixel_value_range

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"

def test_pgm_median_brightness_type():
    samples = list(_PGM.glob("*.pgm"))
    assert samples
    r = pgm_median_brightness(samples[0])
    assert isinstance(r, float)

def test_pgm_median_brightness_non_negative():
    for s in _PGM.glob("*.pgm"):
        assert pgm_median_brightness(s) >= 0.0

def test_pgm_pixel_value_range_type():
    samples = list(_PGM.glob("*.pgm"))
    assert samples
    r = pgm_pixel_value_range(samples[0])
    assert isinstance(r, int)

def test_pgm_pixel_value_range_non_negative():
    for s in _PGM.glob("*.pgm"):
        assert pgm_pixel_value_range(s) >= 0

# FODP ------------------------------------------------------------------------
from src.python.fodp.fodp_codec import fodp_shortest_slide_index, fodp_shape_count_variance

_FODP = _REPO / "samples" / "by-format" / "fodp"

def test_fodp_shortest_slide_index_type():
    samples = list(_FODP.glob("*.fodp"))
    assert samples
    r = fodp_shortest_slide_index(samples[0])
    assert isinstance(r, int)

def test_fodp_shortest_slide_index_valid():
    for s in _FODP.glob("*.fodp"):
        r = fodp_shortest_slide_index(s)
        assert r >= -1

def test_fodp_shape_count_variance_type():
    samples = list(_FODP.glob("*.fodp"))
    assert samples
    r = fodp_shape_count_variance(samples[0])
    assert isinstance(r, float)

def test_fodp_shape_count_variance_non_negative():
    for s in _FODP.glob("*.fodp"):
        assert fodp_shape_count_variance(s) >= 0.0

# FODT ------------------------------------------------------------------------
from src.python.fodt.neutral_model import fodt_total_char_count, fodt_heading_to_para_ratio

_FODT = _REPO / "samples" / "by-format" / "fodt"

def test_fodt_total_char_count_type():
    samples = list(_FODT.glob("*.fodt"))
    assert samples
    r = fodt_total_char_count(samples[0])
    assert isinstance(r, int)

def test_fodt_total_char_count_non_negative():
    for s in _FODT.glob("*.fodt"):
        assert fodt_total_char_count(s) >= 0

def test_fodt_heading_to_para_ratio_type():
    samples = list(_FODT.glob("*.fodt"))
    assert samples
    r = fodt_heading_to_para_ratio(samples[0])
    assert isinstance(r, float)

def test_fodt_heading_to_para_ratio_non_negative():
    for s in _FODT.glob("*.fodt"):
        assert fodt_heading_to_para_ratio(s) >= 0.0
