"""Sprint 105 — PBM/PGM/FODP/FODT cycle 9: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_edge_pixel_sum, pbm_center_pixel_value
from src.python.pgm.pgm_parser import pgm_highlight_count, pgm_column_mean
from src.python.fodp.fodp_codec import fodp_avg_text_per_slide, fodp_shape_slide_ratio
from src.python.fodt.neutral_model import fodt_heading_text_ratio, fodt_longest_heading_length

_PBM = next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
_PGM = next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_FODP = next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
_FODT = next((_REPO / "samples" / "by-format" / "fodt").glob("*.fodt"))


# --- PBM ---
def test_pbm_edge_pixel_sum_importable():
    assert callable(pbm_edge_pixel_sum)

def test_pbm_edge_pixel_sum_returns_int():
    result = pbm_edge_pixel_sum(_PBM)
    assert isinstance(result, int) and result >= 0

def test_pbm_center_pixel_value_importable():
    assert callable(pbm_center_pixel_value)

def test_pbm_center_pixel_value_returns_int():
    result = pbm_center_pixel_value(_PBM)
    assert isinstance(result, int) and result in (0, 1)


# --- PGM ---
def test_pgm_highlight_count_importable():
    assert callable(pgm_highlight_count)

def test_pgm_highlight_count_returns_int():
    result = pgm_highlight_count(_PGM)
    assert isinstance(result, int) and result >= 0

def test_pgm_column_mean_importable():
    assert callable(pgm_column_mean)

def test_pgm_column_mean_returns_float():
    result = pgm_column_mean(_PGM)
    assert isinstance(result, float) and result >= 0.0


# --- FODP ---
def test_fodp_avg_text_per_slide_importable():
    assert callable(fodp_avg_text_per_slide)

def test_fodp_avg_text_per_slide_returns_float():
    result = fodp_avg_text_per_slide(_FODP)
    assert isinstance(result, (int, float)) and result >= 0.0

def test_fodp_shape_slide_ratio_importable():
    assert callable(fodp_shape_slide_ratio)

def test_fodp_shape_slide_ratio_returns_float():
    result = fodp_shape_slide_ratio(_FODP)
    assert isinstance(result, (int, float)) and result >= 0.0


# --- FODT ---
def test_fodt_heading_text_ratio_importable():
    assert callable(fodt_heading_text_ratio)

def test_fodt_heading_text_ratio_returns_float():
    result = fodt_heading_text_ratio(_FODT)
    assert isinstance(result, float) and 0.0 <= result <= 1.0

def test_fodt_longest_heading_length_importable():
    assert callable(fodt_longest_heading_length)

def test_fodt_longest_heading_length_returns_int():
    result = fodt_longest_heading_length(_FODT)
    assert isinstance(result, int) and result >= 0


# --- Integration ---
def test_all_eight_functions_callable():
    fns = [
        pbm_edge_pixel_sum, pbm_center_pixel_value,
        pgm_highlight_count, pgm_column_mean,
        fodp_avg_text_per_slide, fodp_shape_slide_ratio,
        fodt_heading_text_ratio, fodt_longest_heading_length,
    ]
    assert all(callable(f) for f in fns)
