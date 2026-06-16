"""Sprint 53: PPM ppm_column_count + ppm_min_dimension (R263)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_column_count, ppm_min_dimension

PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"

RED_1X1 = PPM_DIR / "1x1-red.ppm"
RGBW_2X2 = PPM_DIR / "2x2-rgbw.ppm"
GRAD_3X1 = PPM_DIR / "3x1-gradient.ppm"


# --- ppm_column_count ---

def test_column_count_1x1_is_1():
    assert ppm_column_count(RED_1X1) == 1


def test_column_count_2x2_is_2():
    assert ppm_column_count(RGBW_2X2) == 2


def test_column_count_3x1_is_3():
    assert ppm_column_count(GRAD_3X1) == 3


def test_column_count_returns_int():
    assert isinstance(ppm_column_count(RED_1X1), int)


def test_column_count_positive():
    assert ppm_column_count(RED_1X1) > 0
    assert ppm_column_count(GRAD_3X1) > 0


# --- ppm_min_dimension ---

def test_min_dimension_1x1_is_1():
    assert ppm_min_dimension(RED_1X1) == 1


def test_min_dimension_2x2_is_2():
    assert ppm_min_dimension(RGBW_2X2) == 2


def test_min_dimension_3x1_is_1():
    # 3x1: min(3, 1) = 1
    assert ppm_min_dimension(GRAD_3X1) == 1


def test_min_dimension_returns_int():
    assert isinstance(ppm_min_dimension(RED_1X1), int)


def test_min_dimension_le_column_count():
    assert ppm_min_dimension(GRAD_3X1) <= ppm_column_count(GRAD_3X1)


def test_min_dimension_positive():
    assert ppm_min_dimension(RED_1X1) > 0
    assert ppm_min_dimension(RGBW_2X2) > 0
