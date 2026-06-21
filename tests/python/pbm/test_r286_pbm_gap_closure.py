"""
Tests for PBM gap closure (2 FOSS functions).
Closes: GAP-PBM-FOSS-PBM_CORNER_B-001, GAP-PBM-FOSS-PBM_ROW_UNIF-001

Known sample values:
  1x1-black.pbm: corner_black=4, row_uniformity=1.0
  2x2-checker.pbm: corner_black=2, row_uniformity=0.0
  3x2-pattern.pbm: corner_black=2, row_uniformity=0.0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pbm_corner_black_count, pbm_row_uniformity

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = _PBM / "1x1-black.pbm"
_CHECKER = _PBM / "2x2-checker.pbm"
_PATTERN = _PBM / "3x2-pattern.pbm"


class TestPbmCornerBlackCount:
    def test_returns_int(self):
        assert isinstance(pbm_corner_black_count(_BLACK), int)

    def test_nonnegative(self):
        for p in [_BLACK, _CHECKER, _PATTERN]:
            assert pbm_corner_black_count(p) >= 0

    def test_all_black_corner_count(self):
        # 1x1-black: all 4 corners are the same pixel which is black → 4
        assert pbm_corner_black_count(_BLACK) == 4

    def test_checker_corner_count(self):
        # 2x2-checker: 2 black corners
        assert pbm_corner_black_count(_CHECKER) == 2

    def test_pattern_corner_count(self):
        # 3x2-pattern: 2 black corners
        assert pbm_corner_black_count(_PATTERN) == 2

    def test_all_black_higher_than_checker(self):
        assert pbm_corner_black_count(_BLACK) > pbm_corner_black_count(_CHECKER)

    def test_result_bounded_by_four(self):
        for p in [_BLACK, _CHECKER, _PATTERN]:
            assert pbm_corner_black_count(p) <= 4


class TestPbmRowUniformity:
    def test_returns_float(self):
        assert isinstance(pbm_row_uniformity(_BLACK), float)

    def test_bounded_zero_to_one(self):
        for p in [_BLACK, _CHECKER, _PATTERN]:
            r = pbm_row_uniformity(p)
            assert 0.0 <= r <= 1.0

    def test_all_black_is_uniform(self):
        # 1x1-black: all identical → uniformity=1.0
        assert pbm_row_uniformity(_BLACK) == 1.0

    def test_checker_not_uniform(self):
        # alternating pattern → uniformity=0.0
        assert pbm_row_uniformity(_CHECKER) == 0.0

    def test_pattern_not_uniform(self):
        assert pbm_row_uniformity(_PATTERN) == 0.0

    def test_all_return_float(self):
        for p in [_BLACK, _CHECKER, _PATTERN]:
            assert isinstance(pbm_row_uniformity(p), float)
