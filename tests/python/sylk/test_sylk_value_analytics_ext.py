"""Tests for SYLK value analytics extensions in sylk_value_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_value_analytics import (
    sylk_col_count,
    sylk_id_line,
    sylk_all_cells_same_type,
    sylk_has_only_strings,
    sylk_has_only_numeric,
    sylk_first_cell_value,
)

SAMPLES = Path("samples/by-format/sylk/valid")
MINIMAL = SAMPLES / "minimal-2x2.slk"    # 2x2: Name/Value(str),Alpha(str)/42(num) — mixed
NUMERIC = SAMPLES / "numeric-row.slk"    # 1x3: 1,2,3 numeric only
SINGLE  = SAMPLES / "single-cell.slk"   # 1x1: 99 numeric


# --- sylk_col_count ---

def test_col_count_minimal():
    assert sylk_col_count(MINIMAL) == 2


def test_col_count_numeric():
    assert sylk_col_count(NUMERIC) == 3


def test_col_count_single():
    assert sylk_col_count(SINGLE) == 1


def test_col_count_returns_int():
    assert isinstance(sylk_col_count(MINIMAL), int)


# --- sylk_id_line ---

def test_id_line_minimal():
    assert sylk_id_line(MINIMAL) == "ID;P"


def test_id_line_numeric():
    assert sylk_id_line(NUMERIC) == "ID;P"


def test_id_line_returns_str():
    assert isinstance(sylk_id_line(MINIMAL), str)


# --- sylk_all_cells_same_type ---

def test_all_cells_same_type_minimal():
    # minimal-2x2 has mixed types (string + numeric)
    assert sylk_all_cells_same_type(MINIMAL) is False


def test_all_cells_same_type_numeric():
    # numeric-row has only numeric cells
    assert sylk_all_cells_same_type(NUMERIC) is True


def test_all_cells_same_type_returns_bool():
    assert isinstance(sylk_all_cells_same_type(MINIMAL), bool)


# --- sylk_has_only_strings ---

def test_has_only_strings_minimal():
    assert sylk_has_only_strings(MINIMAL) is False


def test_has_only_strings_numeric():
    assert sylk_has_only_strings(NUMERIC) is False


def test_has_only_strings_returns_bool():
    assert isinstance(sylk_has_only_strings(MINIMAL), bool)


# --- sylk_has_only_numeric ---

def test_has_only_numeric_minimal():
    assert sylk_has_only_numeric(MINIMAL) is False


def test_has_only_numeric_numeric():
    assert sylk_has_only_numeric(NUMERIC) is True


def test_has_only_numeric_single():
    assert sylk_has_only_numeric(SINGLE) is True


def test_has_only_numeric_returns_bool():
    assert isinstance(sylk_has_only_numeric(MINIMAL), bool)


# --- sylk_first_cell_value ---

def test_first_cell_value_minimal():
    assert sylk_first_cell_value(MINIMAL) == "Name"


def test_first_cell_value_numeric():
    assert sylk_first_cell_value(NUMERIC) == 1


def test_first_cell_value_single():
    assert sylk_first_cell_value(SINGLE) == 99


def test_first_cell_value_returns_not_none():
    assert sylk_first_cell_value(MINIMAL) is not None
