"""Tests for gnumeric.gnumeric_codec.sum_column() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, set_cell_value, sum_column


def _make_model():
    model = create_gnumeric([{"name": "Sheet1", "cells": []}])
    model = set_cell_value(model, 0, 0, 0, "10")
    model = set_cell_value(model, 0, 1, 0, "20")
    model = set_cell_value(model, 0, 2, 0, "30")
    return model


def test_sum_numeric_column():
    model = _make_model()
    result = sum_column(model, 0, 0)
    assert result == 60.0


def test_sum_returns_float():
    model = _make_model()
    assert isinstance(sum_column(model, 0, 0), float)


def test_sum_empty_column():
    model = create_gnumeric([{"name": "Sheet1", "cells": []}])
    assert sum_column(model, 0, 99) == 0.0


def test_sum_skips_non_numeric():
    model = create_gnumeric([{"name": "Sheet1", "cells": []}])
    model = set_cell_value(model, 0, 0, 0, "5")
    model = set_cell_value(model, 0, 1, 0, "text")
    model = set_cell_value(model, 0, 2, 0, "3")
    assert sum_column(model, 0, 0) == 8.0


def test_out_of_range_sheet():
    model = create_gnumeric([{"name": "Sheet1", "cells": []}])
    assert sum_column(model, 99, 0) == 0.0


def test_negative_values():
    model = create_gnumeric([{"name": "Sheet1", "cells": []}])
    model = set_cell_value(model, 0, 0, 0, "-5")
    model = set_cell_value(model, 0, 1, 0, "10")
    assert sum_column(model, 0, 0) == 5.0
