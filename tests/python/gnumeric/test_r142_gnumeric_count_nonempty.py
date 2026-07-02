"""Tests for gnumeric.gnumeric_codec.count_nonempty_cells() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import GnumericError, count_nonempty_cells, create_gnumeric, set_cell_value


def test_empty_sheet_zero():
    model = create_gnumeric([{"name": "S", "cells": []}])
    assert count_nonempty_cells(model, 0) == 0


def test_one_nonempty_cell():
    model = create_gnumeric([{"name": "S", "cells": []}])
    model = set_cell_value(model, 0, 0, 0, "hello")
    assert count_nonempty_cells(model, 0) == 1


def test_two_nonempty_cells():
    model = create_gnumeric([{"name": "S", "cells": []}])
    model = set_cell_value(model, 0, 0, 0, "a")
    model = set_cell_value(model, 0, 0, 1, "b")
    assert count_nonempty_cells(model, 0) == 2


def test_empty_string_not_counted():
    model = create_gnumeric([{"name": "S", "cells": []}])
    model = set_cell_value(model, 0, 0, 0, "")
    model = set_cell_value(model, 0, 0, 1, "real")
    assert count_nonempty_cells(model, 0) == 1


def test_type_error():
    try:
        count_nonempty_cells("not a dict", 0)
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_index_out_of_range():
    model = create_gnumeric([{"name": "S", "cells": []}])
    try:
        count_nonempty_cells(model, 5)
        assert 1 == 0, "Expected GnumericError"

    except GnumericError:
        pass


def test_negative_index():
    model = create_gnumeric([{"name": "S", "cells": []}])
    try:
        count_nonempty_cells(model, -1)
        assert 1 == 0, "Expected GnumericError"

    except GnumericError:
        pass
