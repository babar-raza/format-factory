"""Tests for gnumeric_has_only_one_column and gnumeric_cells_in_first_column (Sprint 86, R296)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_has_only_one_column, gnumeric_cells_in_first_column

GN = _REPO / "samples" / "by-format" / "gnumeric"


@pytest.fixture
def minimal():
    return GN / "minimal-spreadsheet.gnumeric"


@pytest.fixture
def multi():
    return GN / "multi-cell-basic.gnumeric"


@pytest.fixture
def empty():
    return GN / "empty-sheet.gnumeric"


def test_has_only_one_column_minimal_true(minimal):
    assert gnumeric_has_only_one_column(minimal) is True


def test_has_only_one_column_multi_false(multi):
    assert gnumeric_has_only_one_column(multi) is False


def test_has_only_one_column_empty_false(empty):
    assert gnumeric_has_only_one_column(empty) is False


def test_has_only_one_column_returns_bool(minimal):
    assert isinstance(gnumeric_has_only_one_column(minimal), bool)


def test_cells_in_first_column_minimal(minimal):
    assert gnumeric_cells_in_first_column(minimal) == 1


def test_cells_in_first_column_multi(multi):
    assert gnumeric_cells_in_first_column(multi) == 2


def test_cells_in_first_column_empty(empty):
    assert gnumeric_cells_in_first_column(empty) == 0


def test_cells_in_first_column_returns_int(minimal):
    assert isinstance(gnumeric_cells_in_first_column(minimal), int)


def test_cells_in_first_column_nonnegative(minimal):
    assert gnumeric_cells_in_first_column(minimal) >= 0


def test_has_only_one_column_and_cells_consistent(minimal):
    # Single-column doc should have cells in column 0
    assert gnumeric_has_only_one_column(minimal) is True
    assert gnumeric_cells_in_first_column(minimal) >= 1
