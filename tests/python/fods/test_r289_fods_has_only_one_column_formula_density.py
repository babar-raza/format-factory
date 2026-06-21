"""Tests for fods_has_only_one_column and fods_formula_density (Sprint 79, R289)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.parser import parse_fods_strict
from fods.neutral_model import fods_has_only_one_column, fods_formula_density

FODS = _REPO / "samples" / "by-format" / "fods"


@pytest.fixture
def wb_minimal():
    return parse_fods_strict(FODS / "minimal-spreadsheet.fods")


@pytest.fixture
def wb_formula():
    return parse_fods_strict(FODS / "formula-basic.fods")


@pytest.fixture
def wb_multi():
    return parse_fods_strict(FODS / "multi-sheet-basic.fods")


@pytest.fixture
def wb_typed():
    return parse_fods_strict(FODS / "typed-values-basic.fods")


def test_has_only_one_column_minimal_true(wb_minimal):
    assert fods_has_only_one_column(wb_minimal) is True


def test_has_only_one_column_formula_true(wb_formula):
    assert fods_has_only_one_column(wb_formula) is True


def test_has_only_one_column_multi_false(wb_multi):
    assert fods_has_only_one_column(wb_multi) is False


def test_has_only_one_column_returns_bool(wb_minimal):
    assert isinstance(fods_has_only_one_column(wb_minimal), bool)


def test_formula_density_minimal_zero(wb_minimal):
    assert abs(fods_formula_density(wb_minimal) - 0.0) < 0.001


def test_formula_density_formula_positive(wb_formula):
    assert fods_formula_density(wb_formula) > 0.0


def test_formula_density_formula_value(wb_formula):
    assert abs(fods_formula_density(wb_formula) - 0.25) < 0.001


def test_formula_density_multi_zero(wb_multi):
    assert abs(fods_formula_density(wb_multi) - 0.0) < 0.001


def test_formula_density_returns_float(wb_formula):
    assert isinstance(fods_formula_density(wb_formula), float)


def test_formula_density_between_zero_and_one(wb_typed):
    d = fods_formula_density(wb_typed)
    assert 0.0 <= d <= 1.0
