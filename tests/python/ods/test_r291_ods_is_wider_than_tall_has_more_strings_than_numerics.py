"""Tests for ods_is_wider_than_tall and ods_has_more_strings_than_numerics (Sprint 81, R291)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import ods_is_wider_than_tall, ods_has_more_strings_than_numerics

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


@pytest.fixture
def minimal():
    return ODS / "minimal-spreadsheet.ods"


@pytest.fixture
def numeric():
    return ODS / "numeric-row.ods"


@pytest.fixture
def single():
    return ODS / "single-cell.ods"


def test_is_wider_than_tall_minimal_false(minimal):
    assert ods_is_wider_than_tall(minimal) is False


def test_is_wider_than_tall_numeric_true(numeric):
    assert ods_is_wider_than_tall(numeric) is True


def test_is_wider_than_tall_single_false(single):
    assert ods_is_wider_than_tall(single) is False


def test_is_wider_than_tall_returns_bool(minimal):
    assert isinstance(ods_is_wider_than_tall(minimal), bool)


def test_has_more_strings_minimal_true(minimal):
    assert ods_has_more_strings_than_numerics(minimal) is True


def test_has_more_strings_numeric_false(numeric):
    assert ods_has_more_strings_than_numerics(numeric) is False


def test_has_more_strings_single_true(single):
    assert ods_has_more_strings_than_numerics(single) is True


def test_has_more_strings_returns_bool(numeric):
    assert isinstance(ods_has_more_strings_than_numerics(numeric), bool)


def test_is_wider_consistent_with_col_row_count(numeric):
    from ods.ods_parser import ods_column_count, ods_row_count
    assert ods_is_wider_than_tall(numeric) == (ods_column_count(numeric) > ods_row_count(numeric))


def test_has_more_strings_consistent_with_counts(minimal):
    from ods.ods_parser import ods_string_cell_count, ods_numeric_cell_count
    assert ods_has_more_strings_than_numerics(minimal) == (ods_string_cell_count(minimal) > ods_numeric_cell_count(minimal))
