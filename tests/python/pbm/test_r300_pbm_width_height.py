"""Tests for pbm_width and pbm_height (Sprint 90, R300)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_width, pbm_height

PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


@pytest.fixture
def single():
    return PBM / "1x1-black.pbm"


@pytest.fixture
def checker():
    return PBM / "2x2-checker.pbm"


@pytest.fixture
def pattern():
    return PBM / "3x2-pattern.pbm"


def test_width_single(single):
    assert pbm_width(single) == 1


def test_width_checker(checker):
    assert pbm_width(checker) == 2


def test_width_pattern(pattern):
    assert pbm_width(pattern) == 3


def test_width_returns_int(single):
    assert isinstance(pbm_width(single), int)


def test_width_positive(checker):
    assert pbm_width(checker) > 0


def test_height_single(single):
    assert pbm_height(single) == 1


def test_height_checker(checker):
    assert pbm_height(checker) == 2


def test_height_pattern(pattern):
    assert pbm_height(pattern) == 2


def test_height_returns_int(single):
    assert isinstance(pbm_height(single), int)


def test_height_positive(checker):
    assert pbm_height(checker) > 0
