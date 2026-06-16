"""Tests for pbm_has_any_white and pbm_max_row_black_count (Sprint 42)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_has_any_white, pbm_max_row_black_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")    # 1x1 all black: has_white=False, max_row=1
_CHECKER = str(_DIR / "2x2-checker.pbm") # 2x2 checker: has_white=True, max_row=1
_PATTERN = str(_DIR / "3x2-pattern.pbm") # 3x2 pattern: has_white=True, max_row=2


class TestPbmHasAnyWhite:
    def test_return_type(self):
        assert isinstance(pbm_has_any_white(_BLACK), bool)

    def test_false_for_all_black(self):
        # 1x1-black.pbm: single black pixel, no white pixels
        assert pbm_has_any_white(_BLACK) is False

    def test_true_for_checker(self):
        # 2x2-checker: pixels=[1,0,0,1] — has white pixels
        assert pbm_has_any_white(_CHECKER) is True

    def test_true_for_pattern(self):
        # 3x2-pattern: pixels=[1,0,1,0,1,0] — has white pixels
        assert pbm_has_any_white(_PATTERN) is True

    def test_consistent_across_calls(self):
        assert pbm_has_any_white(_CHECKER) == pbm_has_any_white(_CHECKER)

    def test_false_is_bool_not_none(self):
        result = pbm_has_any_white(_BLACK)
        assert result is False
        assert result is not None


class TestPbmMaxRowBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_max_row_black_count(_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        # 1x1-black: 1 row with 1 black pixel -> max=1
        assert pbm_max_row_black_count(_BLACK) == 1

    def test_exact_1_for_checker(self):
        # 2x2-checker: rows=[1,1] -> max=1
        assert pbm_max_row_black_count(_CHECKER) == 1

    def test_exact_2_for_pattern(self):
        # 3x2-pattern: pixels=[1,0,1,0,1,0] rows=[2,1] -> max=2
        assert pbm_max_row_black_count(_PATTERN) == 2

    def test_nonnegative(self):
        assert pbm_max_row_black_count(_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_max_row_black_count(_PATTERN) == pbm_max_row_black_count(_PATTERN)

    def test_max_cannot_exceed_width(self):
        # max blacks per row <= width
        import sys; sys.path.insert(0, str(_REPO))
        from src.python.pbm import parse_pbm_strict
        img = parse_pbm_strict(_PATTERN)
        assert pbm_max_row_black_count(_PATTERN) <= img.width
