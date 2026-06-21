"""Tests for fods_is_all_string and fods_has_numeric_cells (Sprint 74)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import fods_is_all_string, fods_has_numeric_cells
from fods.parser import parse_fods_strict

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


# --- fods_is_all_string ---

def test_is_all_string_minimal_true(wb_minimal):
    assert fods_is_all_string(wb_minimal) is True


def test_is_all_string_formula_false(wb_formula):
    assert fods_is_all_string(wb_formula) is False


def test_is_all_string_multi_true(wb_multi):
    assert fods_is_all_string(wb_multi) is True


def test_is_all_string_returns_bool(wb_minimal):
    assert isinstance(fods_is_all_string(wb_minimal), bool)


def test_is_all_string_empty_workbook():
    wb = {"sheets": []}
    assert fods_is_all_string(wb) is True


# --- fods_has_numeric_cells ---

def test_has_numeric_cells_minimal_false(wb_minimal):
    assert fods_has_numeric_cells(wb_minimal) is False


def test_has_numeric_cells_formula_true(wb_formula):
    assert fods_has_numeric_cells(wb_formula) is True


def test_has_numeric_cells_multi_false(wb_multi):
    assert fods_has_numeric_cells(wb_multi) is False


def test_has_numeric_cells_returns_bool(wb_formula):
    assert isinstance(fods_has_numeric_cells(wb_formula), bool)


def test_has_numeric_cells_empty_workbook():
    wb = {"sheets": []}
    assert fods_has_numeric_cells(wb) is False
