"""Tests for tsv_numeric_range and tsv_has_only_one_row (Sprint 85, R295)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import tsv_numeric_range, tsv_has_only_one_row

TSV = _REPO / "samples" / "by-format" / "tsv"


@pytest.fixture
def minimal():
    return TSV / "minimal-2x2.tsv"


@pytest.fixture
def multi():
    return TSV / "multi-column.tsv"


@pytest.fixture
def single():
    return TSV / "single-cell.tsv"


def test_numeric_range_minimal(minimal):
    assert abs(tsv_numeric_range(minimal) - 5.0) < 0.001


def test_numeric_range_multi(multi):
    assert abs(tsv_numeric_range(multi) - 94.5) < 0.001


def test_numeric_range_single_zero(single):
    assert abs(tsv_numeric_range(single) - 0.0) < 0.001


def test_numeric_range_returns_float(minimal):
    assert isinstance(tsv_numeric_range(minimal), float)


def test_has_only_one_row_minimal_false(minimal):
    assert tsv_has_only_one_row(minimal) is False


def test_has_only_one_row_multi_false(multi):
    assert tsv_has_only_one_row(multi) is False


def test_has_only_one_row_single_true(single):
    assert tsv_has_only_one_row(single) is True


def test_has_only_one_row_returns_bool(minimal):
    assert isinstance(tsv_has_only_one_row(minimal), bool)


def test_numeric_range_nonnegative(minimal):
    assert tsv_numeric_range(minimal) >= 0.0


def test_has_only_one_row_multi_col_false(multi):
    assert tsv_has_only_one_row(multi) is not True
