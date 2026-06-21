"""Tests for csv_numeric_field_ratio and csv_value_sum (Sprint 87, R297)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_numeric_field_ratio, csv_value_sum

CSV = _REPO / "samples" / "by-format" / "csv"


@pytest.fixture
def minimal():
    return CSV / "minimal-2x2.csv"


@pytest.fixture
def quoted():
    return CSV / "quoted-fields.csv"


@pytest.fixture
def single():
    return CSV / "single-cell.csv"


def test_numeric_field_ratio_minimal(minimal):
    assert abs(csv_numeric_field_ratio(minimal) - 0.5) < 0.001


def test_numeric_field_ratio_quoted(quoted):
    assert abs(csv_numeric_field_ratio(quoted) - (1/3)) < 0.001


def test_numeric_field_ratio_single(single):
    assert abs(csv_numeric_field_ratio(single) - 1.0) < 0.001


def test_numeric_field_ratio_returns_float(minimal):
    assert isinstance(csv_numeric_field_ratio(minimal), float)


def test_value_sum_minimal(minimal):
    assert abs(csv_value_sum(minimal) - 55.0) < 0.01


def test_value_sum_quoted(quoted):
    assert abs(csv_value_sum(quoted) - 29.98) < 0.01


def test_value_sum_single(single):
    assert abs(csv_value_sum(single) - 42.0) < 0.001


def test_value_sum_returns_float(minimal):
    assert isinstance(csv_value_sum(minimal), float)


def test_numeric_field_ratio_between_0_and_1(minimal):
    ratio = csv_numeric_field_ratio(minimal)
    assert 0.0 <= ratio <= 1.0


def test_value_sum_positive_for_all_numeric(single):
    assert csv_value_sum(single) > 0.0
