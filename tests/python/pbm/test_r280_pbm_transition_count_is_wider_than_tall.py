"""Tests for pbm_transition_count and pbm_is_wider_than_tall (Sprint 70)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from pbm.pbm_parser import pbm_transition_count, pbm_is_wider_than_tall

PBM = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "pbm" / "valid"


class TestPbmTransitionCount:
    def test_single_pixel(self):
        assert pbm_transition_count(PBM / "1x1-black.pbm") == 0

    def test_checker(self):
        assert pbm_transition_count(PBM / "2x2-checker.pbm") == 2

    def test_alternating_pattern(self):
        assert pbm_transition_count(PBM / "3x2-pattern.pbm") == 5

    def test_returns_int(self):
        assert isinstance(pbm_transition_count(PBM / "1x1-black.pbm"), int)

    def test_nonnegative(self):
        for f in ["1x1-black.pbm", "2x2-checker.pbm", "3x2-pattern.pbm"]:
            assert pbm_transition_count(PBM / f) >= 0


class TestPbmIsWiderThanTall:
    def test_square_single(self):
        assert pbm_is_wider_than_tall(PBM / "1x1-black.pbm") is False

    def test_square_two_by_two(self):
        assert pbm_is_wider_than_tall(PBM / "2x2-checker.pbm") is False

    def test_wider_rectangle(self):
        assert pbm_is_wider_than_tall(PBM / "3x2-pattern.pbm") is True

    def test_returns_bool(self):
        assert isinstance(pbm_is_wider_than_tall(PBM / "1x1-black.pbm"), bool)

    def test_all_files_return_bool(self):
        for f in ["1x1-black.pbm", "2x2-checker.pbm", "3x2-pattern.pbm"]:
            assert isinstance(pbm_is_wider_than_tall(PBM / f), bool)
