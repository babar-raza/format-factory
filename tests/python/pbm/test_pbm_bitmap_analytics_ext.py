"""Tests for extended PBM bitmap analytics (pbm_row_transition_count, etc.)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

CHECKER = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"

from src.python.pbm.bitmap_image import (
    pbm_row_transition_count,
    pbm_max_black_run_length,
    pbm_black_run_count,
    pbm_row_black_ratio_variance,
    pbm_edge_black_ratio,
    pbm_isolation_score,
)


class TestPbmRowTransitionCount:
    def test_returns_int(self):
        assert isinstance(pbm_row_transition_count(CHECKER), int)

    def test_nonnegative(self):
        assert pbm_row_transition_count(CHECKER) >= 0

    def test_checker_has_transitions(self):
        # 2x2 checker: each row has 1 transition
        assert pbm_row_transition_count(CHECKER) >= 1

    def test_accepts_string_path(self):
        assert isinstance(pbm_row_transition_count(str(CHECKER)), int)


class TestPbmMaxBlackRunLength:
    def test_returns_int(self):
        assert isinstance(pbm_max_black_run_length(CHECKER), int)

    def test_nonnegative(self):
        assert pbm_max_black_run_length(CHECKER) >= 0

    def test_checker_single_isolated_blacks(self):
        # 2x2 checker: no two adjacent blacks in a row
        assert pbm_max_black_run_length(CHECKER) == 1

    def test_accepts_string_path(self):
        assert isinstance(pbm_max_black_run_length(str(CHECKER)), int)


class TestPbmBlackRunCount:
    def test_returns_int(self):
        assert isinstance(pbm_black_run_count(CHECKER), int)

    def test_nonnegative(self):
        assert pbm_black_run_count(CHECKER) >= 0

    def test_checker_has_runs(self):
        # 2x2 checker: 1 black per row = 1 run per row
        assert pbm_black_run_count(CHECKER) >= 1

    def test_accepts_string_path(self):
        assert isinstance(pbm_black_run_count(str(CHECKER)), int)


class TestPbmRowBlackRatioVariance:
    def test_returns_float(self):
        assert isinstance(pbm_row_black_ratio_variance(CHECKER), float)

    def test_nonnegative(self):
        assert pbm_row_black_ratio_variance(CHECKER) >= 0.0

    def test_checker_uniform_rows(self):
        # 2x2 checker: each row has same black ratio → variance = 0
        assert pbm_row_black_ratio_variance(CHECKER) == 0.0

    def test_accepts_string_path(self):
        assert isinstance(pbm_row_black_ratio_variance(str(CHECKER)), float)


class TestPbmEdgeBlackRatio:
    def test_returns_float(self):
        assert isinstance(pbm_edge_black_ratio(CHECKER), float)

    def test_in_unit_range(self):
        v = pbm_edge_black_ratio(CHECKER)
        assert 0.0 <= v <= 1.0

    def test_checker_has_black_border(self):
        assert pbm_edge_black_ratio(CHECKER) > 0.0

    def test_accepts_string_path(self):
        assert isinstance(pbm_edge_black_ratio(str(CHECKER)), float)


class TestPbmIsolationScore:
    def test_returns_float(self):
        assert isinstance(pbm_isolation_score(CHECKER), float)

    def test_in_unit_range(self):
        v = pbm_isolation_score(CHECKER)
        assert 0.0 <= v <= 1.0

    def test_checker_all_isolated(self):
        # 2x2 checker: no black pixel touches another black pixel
        assert pbm_isolation_score(CHECKER) == 1.0

    def test_accepts_string_path(self):
        assert isinstance(pbm_isolation_score(str(CHECKER)), float)
