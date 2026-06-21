"""Tests for dif_numeric_range and dif_value_sum (Sprint 88, R298)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_numeric_range, dif_value_sum

DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


@pytest.fixture
def minimal():
    return DIF / "minimal-2x2.dif"


@pytest.fixture
def numeric_row():
    return DIF / "numeric-row.dif"


@pytest.fixture
def single():
    return DIF / "single-cell.dif"


def test_numeric_range_minimal(minimal):
    assert abs(dif_numeric_range(minimal) - 57.0) < 0.01


def test_numeric_range_numeric_row(numeric_row):
    assert abs(dif_numeric_range(numeric_row) - 2.0) < 0.01


def test_numeric_range_single(single):
    assert abs(dif_numeric_range(single) - 0.0) < 0.01


def test_numeric_range_returns_float(minimal):
    assert isinstance(dif_numeric_range(minimal), float)


def test_numeric_range_nonnegative(minimal):
    assert dif_numeric_range(minimal) >= 0.0


def test_value_sum_minimal(minimal):
    assert abs(dif_value_sum(minimal) - 141.0) < 0.01


def test_value_sum_numeric_row(numeric_row):
    assert abs(dif_value_sum(numeric_row) - 6.0) < 0.01


def test_value_sum_single(single):
    assert abs(dif_value_sum(single) - 42.0) < 0.01


def test_value_sum_returns_float(minimal):
    assert isinstance(dif_value_sum(minimal), float)


def test_value_sum_positive_for_numeric(numeric_row):
    assert dif_value_sum(numeric_row) > 0.0
