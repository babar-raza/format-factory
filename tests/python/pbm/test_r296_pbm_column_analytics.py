"""Tests for pbm_black_column_count and pbm_max_row_white_count (Sprint r296)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_black_column_count, pbm_max_row_white_count

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


class TestPbmBlackColumnCount:
    """Tests for pbm_black_column_count."""

    def test_1x1_black_has_one_black_column(self):
        """1x1-black.pbm has 1 column and it is black."""
        result = pbm_black_column_count(_PBM / "1x1-black.pbm")
        assert result == 1

    def test_2x2_checker_has_two_black_columns(self):
        """2x2-checker.pbm has 2 columns, each with a black pixel."""
        result = pbm_black_column_count(_PBM / "2x2-checker.pbm")
        assert result == 2

    def test_3x2_pattern_has_three_black_columns(self):
        """3x2-pattern.pbm has 3 columns all containing black pixels."""
        result = pbm_black_column_count(_PBM / "3x2-pattern.pbm")
        assert result == 3

    def test_returns_int(self):
        result = pbm_black_column_count(_PBM / "1x1-black.pbm")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-black.pbm", "2x2-checker.pbm", "3x2-pattern.pbm"]:
            assert pbm_black_column_count(_PBM / f) >= 0

    def test_wider_image_has_more_black_columns(self):
        r1 = pbm_black_column_count(_PBM / "1x1-black.pbm")
        r2 = pbm_black_column_count(_PBM / "3x2-pattern.pbm")
        assert r2 > r1


class TestPbmMaxRowWhiteCount:
    """Tests for pbm_max_row_white_count."""

    def test_1x1_black_has_zero_white_in_row(self):
        """1x1-black.pbm has a single black pixel — no white pixels."""
        result = pbm_max_row_white_count(_PBM / "1x1-black.pbm")
        assert result == 0

    def test_2x2_checker_max_row_white_is_one(self):
        """2x2-checker.pbm rows are [1,0] and [0,1], each with 1 white."""
        result = pbm_max_row_white_count(_PBM / "2x2-checker.pbm")
        assert result == 1

    def test_3x2_pattern_max_row_white_is_two(self):
        """3x2-pattern.pbm row [0,1,0] has 2 white pixels."""
        result = pbm_max_row_white_count(_PBM / "3x2-pattern.pbm")
        assert result == 2

    def test_returns_int(self):
        result = pbm_max_row_white_count(_PBM / "2x2-checker.pbm")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-black.pbm", "2x2-checker.pbm", "3x2-pattern.pbm"]:
            assert pbm_max_row_white_count(_PBM / f) >= 0

    def test_larger_image_has_more_max_white(self):
        r1 = pbm_max_row_white_count(_PBM / "1x1-black.pbm")
        r2 = pbm_max_row_white_count(_PBM / "3x2-pattern.pbm")
        assert r2 > r1
