"""Sprint 113 — PBM/PGM/FODP/FODT cycle 11: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_column_density_avg, pbm_diagonal_pixel_sum
from src.python.pgm.pgm_parser import pgm_border_mean, pgm_pixel_density_ratio
from src.python.fodp.fodp_codec import fodp_total_shape_area, fodp_notes_length_sum
from src.python.fodt.neutral_model import fodt_char_per_word, fodt_heading_word_ratio

_PBM = next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
_PGM = next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_FODP = next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
_FODT = next((_REPO / "samples" / "by-format" / "fodt").glob("*.fodt"))


# --- PBM ---
def test_pbm_column_density_avg_importable():
    assert callable(pbm_column_density_avg)

def test_pbm_column_density_avg_returns_float():
    result = pbm_column_density_avg(_PBM)
    assert isinstance(result, float) and 0.0 <= result <= 1.0

def test_pbm_diagonal_pixel_sum_importable():
    assert callable(pbm_diagonal_pixel_sum)

def test_pbm_diagonal_pixel_sum_returns_int():
    result = pbm_diagonal_pixel_sum(_PBM)
    assert isinstance(result, int) and result >= 0


# --- PGM ---
def test_pgm_border_mean_importable():
    assert callable(pgm_border_mean)

def test_pgm_border_mean_returns_float():
    result = pgm_border_mean(_PGM)
    assert isinstance(result, (int, float)) and result >= 0

def test_pgm_pixel_density_ratio_importable():
    assert callable(pgm_pixel_density_ratio)

def test_pgm_pixel_density_ratio_returns_float():
    result = pgm_pixel_density_ratio(_PGM)
    assert isinstance(result, float) and 0.0 <= result <= 1.0


# --- FODP ---
def test_fodp_total_shape_area_importable():
    assert callable(fodp_total_shape_area)

def test_fodp_total_shape_area_returns_int():
    result = fodp_total_shape_area(_FODP)
    assert isinstance(result, int) and result >= 0

def test_fodp_notes_length_sum_importable():
    assert callable(fodp_notes_length_sum)

def test_fodp_notes_length_sum_returns_int():
    result = fodp_notes_length_sum(_FODP)
    assert isinstance(result, int) and result >= 0


# --- FODT ---
def test_fodt_char_per_word_importable():
    assert callable(fodt_char_per_word)

def test_fodt_char_per_word_returns_float():
    result = fodt_char_per_word(_FODT)
    assert isinstance(result, (int, float)) and result >= 0

def test_fodt_heading_word_ratio_importable():
    assert callable(fodt_heading_word_ratio)

def test_fodt_heading_word_ratio_returns_float():
    result = fodt_heading_word_ratio(_FODT)
    assert isinstance(result, float) and 0.0 <= result <= 1.0
