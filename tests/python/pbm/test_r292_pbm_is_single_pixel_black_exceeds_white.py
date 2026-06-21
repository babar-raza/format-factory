"""Tests for pbm_is_single_pixel and pbm_black_exceeds_white (Sprint 82, R292)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pbm_is_single_pixel, pbm_black_exceeds_white

PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


@pytest.fixture
def black1():
    return PBM / "1x1-black.pbm"


@pytest.fixture
def checker():
    return PBM / "2x2-checker.pbm"


@pytest.fixture
def pattern():
    return PBM / "3x2-pattern.pbm"


def test_is_single_pixel_1x1_true(black1):
    assert pbm_is_single_pixel(black1) is True


def test_is_single_pixel_checker_false(checker):
    assert pbm_is_single_pixel(checker) is False


def test_is_single_pixel_pattern_false(pattern):
    assert pbm_is_single_pixel(pattern) is False


def test_is_single_pixel_returns_bool(black1):
    assert isinstance(pbm_is_single_pixel(black1), bool)


def test_black_exceeds_white_1x1_true(black1):
    assert pbm_black_exceeds_white(black1) is True


def test_black_exceeds_white_checker_false(checker):
    assert pbm_black_exceeds_white(checker) is False


def test_black_exceeds_white_pattern_false(pattern):
    assert pbm_black_exceeds_white(pattern) is False


def test_black_exceeds_white_returns_bool(black1):
    assert isinstance(pbm_black_exceeds_white(black1), bool)


def test_single_pixel_consistent_with_total_count(black1):
    from pbm.pbm_parser import pbm_total_pixel_count
    assert pbm_is_single_pixel(black1) == (pbm_total_pixel_count(black1) == 1)


def test_black_exceeds_consistent_with_counts(checker):
    from pbm.pbm_parser import pbm_black_pixel_count, pbm_white_pixel_count
    assert pbm_black_exceeds_white(checker) == (pbm_black_pixel_count(checker) > pbm_white_pixel_count(checker))
