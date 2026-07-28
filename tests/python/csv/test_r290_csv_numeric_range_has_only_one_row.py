"""Tests for csv_numeric_range and csv_has_only_one_row (Sprint 80, R290)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _ff_csv_loader import ff_csv as m

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


def test_numeric_range_minimal(minimal):
    assert abs(m.csv_numeric_range(minimal) - 5.0) < 0.01


def test_numeric_range_quoted(quoted):
    assert abs(m.csv_numeric_range(quoted) - 10.0) < 0.01


def test_numeric_range_single_cell_zero(single):
    assert abs(m.csv_numeric_range(single) - 0.0) < 0.01


def test_numeric_range_returns_float(minimal):
    assert isinstance(m.csv_numeric_range(minimal), float)


def test_numeric_range_nonnegative(quoted):
    assert m.csv_numeric_range(quoted) >= 0.0


def test_has_only_one_row_minimal_false(minimal):
    assert m.csv_has_only_one_row(minimal) is False


def test_has_only_one_row_quoted_false(quoted):
    assert m.csv_has_only_one_row(quoted) is False


def test_has_only_one_row_single_true(single):
    assert m.csv_has_only_one_row(single) is True


def test_has_only_one_row_returns_bool(single):
    assert isinstance(m.csv_has_only_one_row(single), bool)


def test_has_only_one_row_consistent_with_row_count(single):
    assert m.csv_has_only_one_row(single) == (m.csv_row_count(single) == 1)
