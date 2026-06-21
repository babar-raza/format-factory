"""Tests for PGM Sprint 45 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_HAS_ONLY-001  (Pgm Has Only Extremes)
  GAP-PGM-FOSS-PGM_HIGHLIGH-001  (Pgm Highlight Count)
  GAP-PGM-FOSS-PGM_COLUMN_M-001  (Pgm Column Mean)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_has_only_extremes, pgm_highlight_count, pgm_column_mean

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE_1X1 = str(_DIR / "1x1-white.pgm")
_GRADIENT_2X2 = str(_DIR / "2x2-gradient.pgm")
_RAMP_3X1 = str(_DIR / "3x1-ramp.pgm")


class TestPgmHasOnlyExtremes:
    def test_return_type(self):
        assert isinstance(pgm_has_only_extremes(_WHITE_1X1), bool)

    def test_true_for_all_white_1x1(self):
        assert pgm_has_only_extremes(_WHITE_1X1) is True

    def test_false_for_gradient_2x2(self):
        assert pgm_has_only_extremes(_GRADIENT_2X2) is False

    def test_false_for_ramp(self):
        assert pgm_has_only_extremes(_RAMP_3X1) is False

    def test_consistent_across_calls(self):
        assert pgm_has_only_extremes(_WHITE_1X1) == pgm_has_only_extremes(_WHITE_1X1)


class TestPgmHighlightCount:
    def test_return_type(self):
        assert isinstance(pgm_highlight_count(_WHITE_1X1), int)

    def test_exact_1_for_1x1_white(self):
        assert pgm_highlight_count(_WHITE_1X1) == 1

    def test_exact_2_for_2x2_gradient(self):
        assert pgm_highlight_count(_GRADIENT_2X2) == 2

    def test_nonnegative(self):
        assert pgm_highlight_count(_WHITE_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_highlight_count(_WHITE_1X1) == pgm_highlight_count(_WHITE_1X1)


class TestPgmColumnMean:
    def test_return_type(self):
        assert isinstance(pgm_column_mean(_WHITE_1X1), (int, float))

    def test_exact_255_for_1x1_white(self):
        assert pgm_column_mean(_WHITE_1X1) == 255.0

    def test_exact_127_5_for_gradient(self):
        assert pgm_column_mean(_GRADIENT_2X2) == 127.5

    def test_in_valid_range(self):
        assert 0 <= pgm_column_mean(_WHITE_1X1) <= 255

    def test_consistent_across_calls(self):
        assert pgm_column_mean(_WHITE_1X1) == pgm_column_mean(_WHITE_1X1)
