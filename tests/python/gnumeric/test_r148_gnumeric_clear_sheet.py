"""Tests for gnumeric.gnumeric_codec.clear_sheet() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import clear_sheet, create_gnumeric, fill_column, get_all_values


def test_clears_cells():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, ["a", "b"])
    cleared = clear_sheet(model, 0)
    assert get_all_values(cleared, 0) == []


def test_returns_dict():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    assert isinstance(clear_sheet(model, 0), dict)


def test_does_not_mutate_original():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, ["x"])
    clear_sheet(model, 0)
    assert len(get_all_values(model, 0)) == 1


def test_out_of_range_returns_model():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    result = clear_sheet(model, 99)
    assert result["sheets"] == model["sheets"]


def test_other_sheets_unaffected():
    model = create_gnumeric([{"name": "S1", "cells": []}, {"name": "S2", "cells": []}])
    model = fill_column(model, 0, 0, ["a"])
    model = fill_column(model, 1, 0, ["b"])
    cleared = clear_sheet(model, 0)
    assert get_all_values(cleared, 1) == ["b"]
