"""Tests for gnumeric.gnumeric_codec.fill_column() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, fill_column, get_cell_value


def test_fill_populates_cells():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, ["alpha", "beta", "gamma"])
    assert get_cell_value(model, 0, 0, 0) == "alpha"
    assert get_cell_value(model, 0, 1, 0) == "beta"
    assert get_cell_value(model, 0, 2, 0) == "gamma"


def test_fill_second_column():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 1, ["x", "y"])
    assert get_cell_value(model, 0, 0, 1) == "x"
    assert get_cell_value(model, 0, 1, 1) == "y"


def test_fill_empty_values():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, [])
    # No cells added; cell_grid stays empty
    assert get_cell_value(model, 0, 0, 0) == ""


def test_out_of_range_sheet_returns_model():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    result = fill_column(model, 99, 0, ["v"])
    assert result["sheets"] == model["sheets"]


def test_returns_dict():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    result = fill_column(model, 0, 0, ["a"])
    assert isinstance(result, dict)


def test_does_not_mutate_original():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    fill_column(model, 0, 0, ["changed"])
    assert get_cell_value(model, 0, 0, 0) == ""
