"""Tests for dif_has_mixed_types and dif_nonempty_cell_count (Sprint 80, R290)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_has_mixed_types, dif_nonempty_cell_count

DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


@pytest.fixture
def minimal():
    return DIF / "minimal-2x2.dif"


@pytest.fixture
def numeric():
    return DIF / "numeric-row.dif"


@pytest.fixture
def single():
    return DIF / "single-cell.dif"


def test_has_mixed_types_minimal_true(minimal):
    assert dif_has_mixed_types(minimal) is True


def test_has_mixed_types_numeric_false(numeric):
    assert dif_has_mixed_types(numeric) is False


def test_has_mixed_types_single_false(single):
    assert dif_has_mixed_types(single) is False


def test_has_mixed_types_returns_bool(minimal):
    assert isinstance(dif_has_mixed_types(minimal), bool)


def test_nonempty_cell_count_minimal(minimal):
    assert dif_nonempty_cell_count(minimal) == 8


def test_nonempty_cell_count_numeric(numeric):
    assert dif_nonempty_cell_count(numeric) == 3


def test_nonempty_cell_count_single(single):
    assert dif_nonempty_cell_count(single) == 1


def test_nonempty_cell_count_returns_int(minimal):
    assert isinstance(dif_nonempty_cell_count(minimal), int)


def test_nonempty_cell_count_nonnegative(single):
    assert dif_nonempty_cell_count(single) >= 0


def test_mixed_types_implies_string_and_numeric(minimal):
    from dif.dif_parser import dif_has_string_cells, dif_numeric_cell_count
    if dif_has_mixed_types(minimal):
        assert dif_has_string_cells(minimal) and dif_numeric_cell_count(minimal) > 0
