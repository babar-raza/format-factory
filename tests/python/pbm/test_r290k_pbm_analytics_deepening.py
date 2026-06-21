"""Tests for PBM analytics deepening (R290K): quadrant_black_ratio, horizontal_symmetry, run_length_avg."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pbm_quadrant_black_ratio, pbm_horizontal_symmetry, pbm_run_length_avg

SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"


def test_quadrant_black_ratio_returns_four_values():
    result = pbm_quadrant_black_ratio(SAMPLES / "2x2-checker.pbm")
    assert isinstance(result, list)
    assert len(result) == 4
    for v in result:
        assert 0.0 <= v <= 1.0


def test_quadrant_black_ratio_1x1():
    result = pbm_quadrant_black_ratio(SAMPLES / "1x1-black.pbm")
    assert isinstance(result, list)
    assert len(result) == 4


def test_horizontal_symmetry_returns_float():
    result = pbm_horizontal_symmetry(SAMPLES / "2x2-checker.pbm")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_horizontal_symmetry_1x1():
    result = pbm_horizontal_symmetry(SAMPLES / "1x1-black.pbm")
    assert result == 1.0  # single pixel is always symmetric


def test_run_length_avg_returns_float():
    result = pbm_run_length_avg(SAMPLES / "3x2-pattern.pbm")
    assert isinstance(result, float)
    assert result > 0.0


def test_run_length_avg_1x1():
    result = pbm_run_length_avg(SAMPLES / "1x1-black.pbm")
    assert result == 1.0  # single pixel = 1 run of length 1
