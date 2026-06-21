"""Tests for fods_cells_per_sheet_avg and fods_is_fully_numeric (Sprint 89, R299)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_cells_per_sheet_avg, fods_is_fully_numeric

FODS = _REPO / "samples" / "by-format" / "fods"


@pytest.fixture
def minimal():
    return FODS / "minimal-spreadsheet.fods"


@pytest.fixture
def formula():
    return FODS / "formula-basic.fods"


@pytest.fixture
def multi():
    return FODS / "multi-sheet-basic.fods"


def test_cells_per_sheet_avg_minimal(minimal):
    assert abs(fods_cells_per_sheet_avg(minimal) - 1.0) < 0.01


def test_cells_per_sheet_avg_formula(formula):
    assert abs(fods_cells_per_sheet_avg(formula) - 4.0) < 0.01


def test_cells_per_sheet_avg_multi(multi):
    assert abs(fods_cells_per_sheet_avg(multi) - 2.5) < 0.01


def test_cells_per_sheet_avg_returns_float(minimal):
    assert isinstance(fods_cells_per_sheet_avg(minimal), float)


def test_cells_per_sheet_avg_positive(formula):
    assert fods_cells_per_sheet_avg(formula) > 0.0


def test_is_fully_numeric_minimal(minimal):
    assert fods_is_fully_numeric(minimal) is False


def test_is_fully_numeric_formula(formula):
    assert fods_is_fully_numeric(formula) is True


def test_is_fully_numeric_multi(multi):
    assert fods_is_fully_numeric(multi) is False


def test_is_fully_numeric_returns_bool(minimal):
    assert isinstance(fods_is_fully_numeric(minimal), bool)


def test_is_fully_numeric_consistent_with_formula(formula):
    # formula-basic.fods has all numeric cells
    assert fods_is_fully_numeric(formula) is True
