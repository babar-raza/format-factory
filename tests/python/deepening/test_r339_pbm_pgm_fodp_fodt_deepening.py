"""Sprint 109 — PBM/PGM/FODP/FODT cycle 10: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_row_density_avg, pbm_interior_black_count
from src.python.pgm.pgm_parser import pgm_row_mean, pgm_pixel_quartile_count
from src.python.fodp.fodp_codec import fodp_blank_slide_count, fodp_slide_word_variance
from src.python.fodt.neutral_model import fodt_min_heading_length, fodt_paragraph_density

_PBM = next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
_PGM = next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_FODP = next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
_FODT = next((_REPO / "samples" / "by-format" / "fodt").glob("*.fodt"))


# --- PBM ---
def test_pbm_row_density_avg_importable():
    assert callable(pbm_row_density_avg)

def test_pbm_row_density_avg_returns_float():
    result = pbm_row_density_avg(_PBM)
    assert isinstance(result, float) and 0.0 <= result <= 1.0

def test_pbm_interior_black_count_importable():
    assert callable(pbm_interior_black_count)

def test_pbm_interior_black_count_returns_int():
    result = pbm_interior_black_count(_PBM)
    assert isinstance(result, int) and result >= 0


# --- PGM ---
def test_pgm_row_mean_importable():
    assert callable(pgm_row_mean)

def test_pgm_row_mean_returns_float():
    result = pgm_row_mean(_PGM)
    assert isinstance(result, float) and result >= 0.0

def test_pgm_pixel_quartile_count_importable():
    assert callable(pgm_pixel_quartile_count)

def test_pgm_pixel_quartile_count_returns_int():
    result = pgm_pixel_quartile_count(_PGM)
    assert isinstance(result, int) and 0 <= result <= 4


# --- FODP ---
def test_fodp_blank_slide_count_importable():
    assert callable(fodp_blank_slide_count)

def test_fodp_blank_slide_count_returns_int():
    result = fodp_blank_slide_count(_FODP)
    assert isinstance(result, int) and result >= 0

def test_fodp_slide_word_variance_importable():
    assert callable(fodp_slide_word_variance)

def test_fodp_slide_word_variance_returns_float():
    result = fodp_slide_word_variance(_FODP)
    assert isinstance(result, (int, float)) and result >= 0.0


# --- FODT ---
def test_fodt_min_heading_length_importable():
    assert callable(fodt_min_heading_length)

def test_fodt_min_heading_length_returns_int():
    result = fodt_min_heading_length(_FODT)
    assert isinstance(result, int) and result >= 0

def test_fodt_paragraph_density_importable():
    assert callable(fodt_paragraph_density)

def test_fodt_paragraph_density_returns_float():
    result = fodt_paragraph_density(_FODT)
    assert isinstance(result, float) and result >= 0.0


# --- Integration ---
def test_all_eight_functions_callable():
    fns = [
        pbm_row_density_avg, pbm_interior_black_count,
        pgm_row_mean, pgm_pixel_quartile_count,
        fodp_blank_slide_count, fodp_slide_word_variance,
        fodt_min_heading_length, fodt_paragraph_density,
    ]
    assert all(callable(f) for f in fns)
