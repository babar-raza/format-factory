"""Tests for gnumeric.gnumeric_codec.sum_row() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, fill_column, sum_row


def _model_with_row():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, ["10"])  # col 0, row 0
    model = fill_column(model, 0, 1, ["20"])  # col 1, row 0
    model = fill_column(model, 0, 2, ["30"])  # col 2, row 0
    return model


def test_sum_row_values():
    model = _model_with_row()
    assert sum_row(model, 0, 0) == 60.0


def test_sum_returns_float():
    model = _model_with_row()
    assert isinstance(sum_row(model, 0, 0), float)


def test_sum_empty_row():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    assert sum_row(model, 0, 99) == 0.0


def test_sum_skips_non_numeric():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, ["5"])
    model = fill_column(model, 0, 1, ["text"])
    model = fill_column(model, 0, 2, ["3"])
    # row 0: cols 0,1,2 → 5 + skip + 3 = 8
    assert sum_row(model, 0, 0) == 8.0


def test_out_of_range_sheet():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    assert sum_row(model, 99, 0) == 0.0
