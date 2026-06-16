"""Sprint 52: PGM pgm_column_count + pgm_is_uniform (R262)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import pgm_column_count, pgm_is_uniform

PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"

WHITE_1X1 = PGM_DIR / "1x1-white.pgm"
GRADIENT_2X2 = PGM_DIR / "2x2-gradient.pgm"
RAMP_3X1 = PGM_DIR / "3x1-ramp.pgm"


# --- pgm_column_count ---

def test_column_count_1x1_is_1():
    assert pgm_column_count(WHITE_1X1) == 1


def test_column_count_2x2_is_2():
    assert pgm_column_count(GRADIENT_2X2) == 2


def test_column_count_3x1_is_3():
    assert pgm_column_count(RAMP_3X1) == 3


def test_column_count_returns_int():
    assert isinstance(pgm_column_count(WHITE_1X1), int)


def test_column_count_positive():
    assert pgm_column_count(WHITE_1X1) > 0
    assert pgm_column_count(RAMP_3X1) > 0


# --- pgm_is_uniform ---

def test_is_uniform_white_returns_true():
    # All pixels are 255, so range is 0 → uniform
    assert pgm_is_uniform(WHITE_1X1) is True


def test_is_uniform_gradient_returns_false():
    # Gradient has varying pixel values → not uniform
    assert pgm_is_uniform(GRADIENT_2X2) is False


def test_is_uniform_ramp_returns_false():
    assert pgm_is_uniform(RAMP_3X1) is False


def test_is_uniform_returns_bool_white():
    assert isinstance(pgm_is_uniform(WHITE_1X1), bool)


def test_is_uniform_returns_bool_gradient():
    assert isinstance(pgm_is_uniform(GRADIENT_2X2), bool)
