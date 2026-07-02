"""Tests for gnumeric.gnumeric_codec.get_column_count() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import GnumericError, create_gnumeric, get_column_count, set_cell_value


def _make_model_with_cells(cells: list[tuple[int, int, str]]) -> dict:
    model = create_gnumeric([{"name": "Test", "cells": []}])
    for row, col, val in cells:
        model = set_cell_value(model, 0, row, col, val)
    return model


def test_empty_sheet_returns_zero():
    model = create_gnumeric([{"name": "Empty", "cells": []}])
    assert get_column_count(model, 0) == 0


def test_single_cell_one_column():
    model = _make_model_with_cells([(0, 0, "a")])
    assert get_column_count(model, 0) == 1


def test_two_cells_same_column():
    model = _make_model_with_cells([(0, 2, "a"), (1, 2, "b")])
    assert get_column_count(model, 0) == 1


def test_two_cells_different_columns():
    model = _make_model_with_cells([(0, 0, "a"), (0, 3, "b")])
    assert get_column_count(model, 0) == 2


def test_multiple_columns():
    model = _make_model_with_cells([(0, 0, "a"), (0, 1, "b"), (0, 2, "c"), (1, 0, "d")])
    assert get_column_count(model, 0) == 3


def test_type_error():
    try:
        get_column_count("not a dict", 0)
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_index_out_of_range():
    model = create_gnumeric([{"name": "Sheet", "cells": []}])
    try:
        get_column_count(model, 5)
        assert 1 == 0, "Expected GnumericError"

    except GnumericError:
        pass


def test_negative_index_error():
    model = create_gnumeric([{"name": "Sheet", "cells": []}])
    try:
        get_column_count(model, -1)
        assert 1 == 0, "Expected GnumericError"

    except GnumericError:
        pass
