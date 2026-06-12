"""
Tests for pbm_white_pixel_count — sprint product-deepening-rnext75.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PBM_SAMPLES = REPO / "samples" / "by-format" / "pbm" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from pbm.pbm_parser import pbm_white_pixel_count


def test_import():
    assert callable(pbm_white_pixel_count)


def test_all_black_returns_zero():
    result = pbm_white_pixel_count(PBM_SAMPLES / "1x1-black.pbm")
    assert result == 0


def test_checker_has_two_white_pixels():
    result = pbm_white_pixel_count(PBM_SAMPLES / "2x2-checker.pbm")
    assert result == 2


def test_pattern_has_three_white_pixels():
    result = pbm_white_pixel_count(PBM_SAMPLES / "3x2-pattern.pbm")
    assert result == 3


def test_returns_int():
    result = pbm_white_pixel_count(PBM_SAMPLES / "2x2-checker.pbm")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = pbm_white_pixel_count(PBM_SAMPLES / "1x1-black.pbm")
    assert result >= 0
