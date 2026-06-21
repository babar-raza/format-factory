"""Tests for PBM Sprint 61 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_QUADRANT-001   (Pbm Quadrant Black Ratio)
  GAP-PBM-FOSS-PBM_HORIZONT-001   (Pbm Horizontal Symmetry)
  GAP-PBM-FOSS-PBM_RUN_LENG-001   (Pbm Run Length Avg)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_quadrant_black_ratio, pbm_horizontal_symmetry, pbm_run_length_avg

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1 = str(_DIR / "1x1-black.pbm")
_2X2 = str(_DIR / "2x2-checker.pbm")
_3X2 = str(_DIR / "3x2-pattern.pbm")


class TestPbmQuadrantBlackRatio:
    def test_return_type(self):
        result = pbm_quadrant_black_ratio(_1X1)
        assert isinstance(result, list)

    def test_length_4(self):
        assert len(pbm_quadrant_black_ratio(_1X1)) == 4

    def test_1x1_black_values(self):
        result = pbm_quadrant_black_ratio(_1X1)
        assert result == [0.0, 0.0, 0.0, 1.0]

    def test_2x2_checker_values(self):
        result = pbm_quadrant_black_ratio(_2X2)
        assert result == [1.0, 0.0, 0.0, 1.0]

    def test_all_between_0_and_1(self):
        for val in pbm_quadrant_black_ratio(_2X2):
            assert 0.0 <= val <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_quadrant_black_ratio(_1X1) == pbm_quadrant_black_ratio(_1X1)


class TestPbmHorizontalSymmetry:
    def test_return_type(self):
        assert isinstance(pbm_horizontal_symmetry(_1X1), (int, float))

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_horizontal_symmetry(_1X1) == 1.0

    def test_exact_0_0_for_2x2_checker(self):
        assert pbm_horizontal_symmetry(_2X2) == 0.0

    def test_exact_1_0_for_3x2_pattern(self):
        assert pbm_horizontal_symmetry(_3X2) == 1.0

    def test_between_0_and_1(self):
        assert 0.0 <= pbm_horizontal_symmetry(_1X1) <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_horizontal_symmetry(_1X1) == pbm_horizontal_symmetry(_1X1)


class TestPbmRunLengthAvg:
    def test_return_type(self):
        assert isinstance(pbm_run_length_avg(_1X1), (int, float))

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_run_length_avg(_1X1) == 1.0

    def test_exact_1_333_for_2x2_checker(self):
        assert pbm_run_length_avg(_2X2) == pytest.approx(1.333, rel=1e-2)

    def test_exact_1_0_for_3x2_pattern(self):
        assert pbm_run_length_avg(_3X2) == 1.0

    def test_positive(self):
        assert pbm_run_length_avg(_1X1) > 0

    def test_consistent_across_calls(self):
        assert pbm_run_length_avg(_1X1) == pbm_run_length_avg(_1X1)
