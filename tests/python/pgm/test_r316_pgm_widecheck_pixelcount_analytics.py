"""
Tests for Sprint r316: pgm_width_exceeds_height, pgm_pixel_count.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_width_exceeds_height, pgm_pixel_count

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


# --- pgm_width_exceeds_height ---

def test_pgm_width_exceeds_height_1x1_false():
    # 1x1: width=1 == height=1 → not strictly greater → False
    assert pgm_width_exceeds_height(_PGM / "1x1-white.pgm") is False


def test_pgm_width_exceeds_height_2x2_false():
    # 2x2: width=2 == height=2 → False
    assert pgm_width_exceeds_height(_PGM / "2x2-gradient.pgm") is False


def test_pgm_width_exceeds_height_3x1_true():
    # 3x1: width=3 > height=1 → True
    assert pgm_width_exceeds_height(_PGM / "3x1-ramp.pgm") is True


def test_pgm_width_exceeds_height_returns_bool_1x1():
    assert isinstance(pgm_width_exceeds_height(_PGM / "1x1-white.pgm"), bool)


def test_pgm_width_exceeds_height_returns_bool_3x1():
    assert isinstance(pgm_width_exceeds_height(_PGM / "3x1-ramp.pgm"), bool)


def test_pgm_width_exceeds_height_all_three():
    results = [
        pgm_width_exceeds_height(_PGM / "1x1-white.pgm"),
        pgm_width_exceeds_height(_PGM / "2x2-gradient.pgm"),
        pgm_width_exceeds_height(_PGM / "3x1-ramp.pgm"),
    ]
    assert results == [False, False, True]


# --- pgm_pixel_count ---

def test_pgm_pixel_count_1x1_one():
    assert pgm_pixel_count(_PGM / "1x1-white.pgm") == 1


def test_pgm_pixel_count_2x2_four():
    assert pgm_pixel_count(_PGM / "2x2-gradient.pgm") == 4


def test_pgm_pixel_count_3x1_three():
    assert pgm_pixel_count(_PGM / "3x1-ramp.pgm") == 3


def test_pgm_pixel_count_returns_int_1x1():
    assert isinstance(pgm_pixel_count(_PGM / "1x1-white.pgm"), int)


def test_pgm_pixel_count_returns_int_2x2():
    assert isinstance(pgm_pixel_count(_PGM / "2x2-gradient.pgm"), int)


def test_pgm_pixel_count_all_three_distinct():
    results = [
        pgm_pixel_count(_PGM / "1x1-white.pgm"),
        pgm_pixel_count(_PGM / "2x2-gradient.pgm"),
        pgm_pixel_count(_PGM / "3x1-ramp.pgm"),
    ]
    assert results == [1, 4, 3]
