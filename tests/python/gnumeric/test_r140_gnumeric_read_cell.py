"""Tests for gnumeric.gnumeric_codec.read_cell() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import GnumericError, create_gnumeric, read_cell, set_cell_value


def _make_model_with_cell(row: int, col: int, val: str) -> dict:
    model = create_gnumeric([{"name": "Test", "cells": []}])
    return set_cell_value(model, 0, row, col, val)


def test_read_existing_cell():
    model = _make_model_with_cell(0, 0, "hello")
    assert read_cell(model, 0, 0, 0) == "hello"


def test_read_empty_cell_returns_none():
    model = create_gnumeric([{"name": "Empty", "cells": []}])
    assert read_cell(model, 0, 5, 5) is None


def test_read_cell_different_coords():
    model = _make_model_with_cell(2, 3, "value")
    assert read_cell(model, 0, 2, 3) == "value"
    assert read_cell(model, 0, 0, 0) is None


def test_read_cell_after_set():
    model = create_gnumeric([{"name": "Sheet", "cells": []}])
    model = set_cell_value(model, 0, 1, 1, "test")
    assert read_cell(model, 0, 1, 1) == "test"


def test_type_error():
    try:
        read_cell("not a dict", 0, 0, 0)
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_index_out_of_range():
    model = create_gnumeric([{"name": "Sheet", "cells": []}])
    try:
        read_cell(model, 99, 0, 0)
        assert 1 == 0, "Expected GnumericError"

    except GnumericError:
        pass


def test_negative_sheet_index():
    model = create_gnumeric([{"name": "Sheet", "cells": []}])
    try:
        read_cell(model, -1, 0, 0)
        assert 1 == 0, "Expected GnumericError"

    except GnumericError:
        pass


def test_read_numeric_value():
    model = _make_model_with_cell(0, 0, "42")
    val = read_cell(model, 0, 0, 0)
    assert val == "42"
