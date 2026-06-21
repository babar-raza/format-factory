"""Tests for ods_avg_string_cell_length and ods_has_numeric_content (Sprint 87, R297)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import ods_avg_string_cell_length, ods_has_numeric_content

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


@pytest.fixture
def minimal():
    return ODS / "minimal-spreadsheet.ods"


@pytest.fixture
def numeric_row():
    return ODS / "numeric-row.ods"


@pytest.fixture
def single():
    return ODS / "single-cell.ods"


def test_avg_string_cell_length_minimal(minimal):
    assert abs(ods_avg_string_cell_length(minimal) - (14/3)) < 0.01


def test_avg_string_cell_length_numeric_zero(numeric_row):
    assert abs(ods_avg_string_cell_length(numeric_row) - 0.0) < 0.001


def test_avg_string_cell_length_single(single):
    assert abs(ods_avg_string_cell_length(single) - 2.0) < 0.001


def test_avg_string_cell_length_returns_float(minimal):
    assert isinstance(ods_avg_string_cell_length(minimal), float)


def test_has_numeric_content_minimal_true(minimal):
    assert ods_has_numeric_content(minimal) is True


def test_has_numeric_content_numeric_row_true(numeric_row):
    assert ods_has_numeric_content(numeric_row) is True


def test_has_numeric_content_single_false(single):
    assert ods_has_numeric_content(single) is False


def test_has_numeric_content_returns_bool(minimal):
    assert isinstance(ods_has_numeric_content(minimal), bool)


def test_avg_string_cell_length_nonnegative(numeric_row):
    assert ods_avg_string_cell_length(numeric_row) >= 0.0


def test_has_numeric_content_and_string_length_consistent(single):
    # single-cell has a string value but no numerics
    assert ods_has_numeric_content(single) is False
    assert ods_avg_string_cell_length(single) > 0.0
