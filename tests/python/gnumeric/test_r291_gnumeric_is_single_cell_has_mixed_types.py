"""Tests for gnumeric_is_single_cell and gnumeric_has_mixed_types (Sprint 81, R291)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_is_single_cell, gnumeric_has_mixed_types

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


def test_is_single_cell_minimal_true(minimal):
    assert gnumeric_is_single_cell(minimal) is True


def test_is_single_cell_multi_false(multi):
    assert gnumeric_is_single_cell(multi) is False


def test_is_single_cell_empty_false(empty):
    assert gnumeric_is_single_cell(empty) is False


def test_is_single_cell_returns_bool(minimal):
    assert isinstance(gnumeric_is_single_cell(minimal), bool)


def test_has_mixed_types_minimal_false(minimal):
    assert gnumeric_has_mixed_types(minimal) is False


def test_has_mixed_types_multi_true(multi):
    assert gnumeric_has_mixed_types(multi) is True


def test_has_mixed_types_empty_false(empty):
    assert gnumeric_has_mixed_types(empty) is False


def test_has_mixed_types_returns_bool(multi):
    assert isinstance(gnumeric_has_mixed_types(multi), bool)


def test_is_single_cell_consistent_with_total_count(minimal):
    from gnumeric.gnumeric_codec import gnumeric_total_cell_count
    assert gnumeric_is_single_cell(minimal) == (gnumeric_total_cell_count(minimal) == 1)


def test_has_mixed_types_implies_both_types(multi):
    from gnumeric.gnumeric_codec import gnumeric_has_string_cells, gnumeric_has_numeric_cells
    if gnumeric_has_mixed_types(multi):
        assert gnumeric_has_string_cells(multi) and gnumeric_has_numeric_cells(multi)
