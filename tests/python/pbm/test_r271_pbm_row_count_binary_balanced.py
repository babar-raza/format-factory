"""Tests for pbm_row_count and pbm_is_binary_balanced (Sprint 61)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from pbm.pbm_parser import pbm_row_count, pbm_is_binary_balanced

PBM = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "pbm" / "valid"


class TestPbmRowCount:
    def test_1x1_black(self):
        assert pbm_row_count(PBM / "1x1-black.pbm") == 1

    def test_2x2_checker(self):
        assert pbm_row_count(PBM / "2x2-checker.pbm") == 2

    def test_3x2_pattern(self):
        assert pbm_row_count(PBM / "3x2-pattern.pbm") == 2

    def test_returns_int(self):
        assert isinstance(pbm_row_count(PBM / "1x1-black.pbm"), int)

    def test_positive(self):
        for f in ["1x1-black.pbm", "2x2-checker.pbm", "3x2-pattern.pbm"]:
            assert pbm_row_count(PBM / f) > 0


class TestPbmIsBinaryBalanced:
    def test_1x1_black_not_balanced(self):
        assert pbm_is_binary_balanced(PBM / "1x1-black.pbm") is False

    def test_2x2_checker_balanced(self):
        assert pbm_is_binary_balanced(PBM / "2x2-checker.pbm") is True

    def test_3x2_pattern_balanced(self):
        assert pbm_is_binary_balanced(PBM / "3x2-pattern.pbm") is True

    def test_returns_bool(self):
        assert isinstance(pbm_is_binary_balanced(PBM / "1x1-black.pbm"), bool)

    def test_all_black_not_balanced(self):
        assert pbm_is_binary_balanced(PBM / "1x1-black.pbm") is False
