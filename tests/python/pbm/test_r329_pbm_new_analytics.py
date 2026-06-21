"""
test_r329_pbm_new_analytics.py
Sprint 65 — 5 new PBM analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    pbm_min_col_black_count,
    pbm_white_row_count,
    pbm_aspect_ratio,
    pbm_total_white_pixels,
    pbm_black_white_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_SAMPLES / "1x1-black.pbm")
_CHECKER = str(_SAMPLES / "2x2-checker.pbm")
_PATTERN = str(_SAMPLES / "3x2-pattern.pbm")


# --- pbm_min_col_black_count ---

class TestPbmMinColBlackCount:
    def test_returns_int(self):
        assert isinstance(pbm_min_col_black_count(_CHECKER), int)

    def test_non_negative(self):
        assert pbm_min_col_black_count(_CHECKER) >= 0

    def test_black_all_black(self):
        assert pbm_min_col_black_count(_BLACK) >= 1

    def test_checker_non_negative(self):
        assert pbm_min_col_black_count(_CHECKER) >= 0

    def test_pattern_non_negative(self):
        assert pbm_min_col_black_count(_PATTERN) >= 0


# --- pbm_white_row_count ---

class TestPbmWhiteRowCount:
    def test_returns_int(self):
        assert isinstance(pbm_white_row_count(_CHECKER), int)

    def test_non_negative(self):
        assert pbm_white_row_count(_CHECKER) >= 0

    def test_black_has_no_white_rows(self):
        assert pbm_white_row_count(_BLACK) == 0

    def test_checker_non_negative(self):
        assert pbm_white_row_count(_CHECKER) >= 0

    def test_pattern_non_negative(self):
        assert pbm_white_row_count(_PATTERN) >= 0


# --- pbm_aspect_ratio ---

class TestPbmAspectRatio:
    def test_returns_float(self):
        assert isinstance(pbm_aspect_ratio(_CHECKER), float)

    def test_black_square(self):
        # 1x1 image has aspect ratio 1.0
        assert pbm_aspect_ratio(_BLACK) == 1.0

    def test_checker_square(self):
        # 2x2 image has aspect ratio 1.0
        assert pbm_aspect_ratio(_CHECKER) == 1.0

    def test_pattern_not_square(self):
        # 3x2 image: width=3, height=2 => 1.5
        assert pbm_aspect_ratio(_PATTERN) == 1.5

    def test_non_negative(self):
        assert pbm_aspect_ratio(_CHECKER) >= 0.0


# --- pbm_total_white_pixels ---

class TestPbmTotalWhitePixels:
    def test_returns_int(self):
        assert isinstance(pbm_total_white_pixels(_CHECKER), int)

    def test_non_negative(self):
        assert pbm_total_white_pixels(_CHECKER) >= 0

    def test_black_has_no_white(self):
        assert pbm_total_white_pixels(_BLACK) == 0

    def test_checker_has_white(self):
        assert pbm_total_white_pixels(_CHECKER) >= 1

    def test_pattern_non_negative(self):
        assert pbm_total_white_pixels(_PATTERN) >= 0


# --- pbm_black_white_ratio ---

class TestPbmBlackWhiteRatio:
    def test_returns_float(self):
        assert isinstance(pbm_black_white_ratio(_CHECKER), float)

    def test_non_negative(self):
        assert pbm_black_white_ratio(_CHECKER) >= 0.0

    def test_all_black_returns_zero(self):
        # All black = no white pixels => 0.0
        assert pbm_black_white_ratio(_BLACK) == 0.0

    def test_checker_non_negative(self):
        assert pbm_black_white_ratio(_CHECKER) >= 0.0

    def test_pattern_non_negative(self):
        assert pbm_black_white_ratio(_PATTERN) >= 0.0
