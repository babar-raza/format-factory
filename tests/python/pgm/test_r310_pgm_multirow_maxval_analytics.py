"""
Tests for Sprint r310: pgm_is_multi_row, pgm_maxval_exceeds_avg.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_is_multi_row, pgm_maxval_exceeds_avg

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


# --- pgm_is_multi_row ---

def test_pgm_is_multi_row_1x1_white_false():
    assert pgm_is_multi_row(_PGM / "1x1-white.pgm") is False


def test_pgm_is_multi_row_2x2_gradient_true():
    assert pgm_is_multi_row(_PGM / "2x2-gradient.pgm") is True


def test_pgm_is_multi_row_3x1_ramp_false():
    assert pgm_is_multi_row(_PGM / "3x1-ramp.pgm") is False


def test_pgm_is_multi_row_returns_bool_1x1():
    assert isinstance(pgm_is_multi_row(_PGM / "1x1-white.pgm"), bool)


def test_pgm_is_multi_row_returns_bool_2x2():
    assert isinstance(pgm_is_multi_row(_PGM / "2x2-gradient.pgm"), bool)


def test_pgm_is_multi_row_all_three_distinct():
    results = [
        pgm_is_multi_row(_PGM / "1x1-white.pgm"),
        pgm_is_multi_row(_PGM / "2x2-gradient.pgm"),
        pgm_is_multi_row(_PGM / "3x1-ramp.pgm"),
    ]
    assert results == [False, True, False]


# --- pgm_maxval_exceeds_avg ---

def test_pgm_maxval_exceeds_avg_1x1_white_false():
    # 1x1-white: maxval=255, avg=255.0, 255 > 255 is False
    assert pgm_maxval_exceeds_avg(_PGM / "1x1-white.pgm") is False


def test_pgm_maxval_exceeds_avg_2x2_gradient_true():
    # 2x2-gradient: maxval=255, avg=127.5, 255 > 127.5 is True
    assert pgm_maxval_exceeds_avg(_PGM / "2x2-gradient.pgm") is True


def test_pgm_maxval_exceeds_avg_3x1_ramp_true():
    # 3x1-ramp: maxval=255, avg=127.67, 255 > 127.67 is True
    assert pgm_maxval_exceeds_avg(_PGM / "3x1-ramp.pgm") is True


def test_pgm_maxval_exceeds_avg_returns_bool_1x1():
    assert isinstance(pgm_maxval_exceeds_avg(_PGM / "1x1-white.pgm"), bool)


def test_pgm_maxval_exceeds_avg_returns_bool_2x2():
    assert isinstance(pgm_maxval_exceeds_avg(_PGM / "2x2-gradient.pgm"), bool)


def test_pgm_maxval_exceeds_avg_all_three():
    results = [
        pgm_maxval_exceeds_avg(_PGM / "1x1-white.pgm"),
        pgm_maxval_exceeds_avg(_PGM / "2x2-gradient.pgm"),
        pgm_maxval_exceeds_avg(_PGM / "3x1-ramp.pgm"),
    ]
    assert results == [False, True, True]
