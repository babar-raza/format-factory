"""Tests for gnumeric.gnumeric_codec.get_all_values() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, fill_column, get_all_values


def test_returns_list():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    assert isinstance(get_all_values(model, 0), list)


def test_empty_sheet():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    assert get_all_values(model, 0) == []


def test_values_present():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, ["a", "b", "c"])
    values = get_all_values(model, 0)
    assert "a" in values
    assert "b" in values
    assert "c" in values


def test_out_of_range_sheet():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    assert get_all_values(model, 99) == []


def test_count_matches_cells():
    model = create_gnumeric([{"name": "S1", "cells": []}])
    model = fill_column(model, 0, 0, ["x", "y"])
    model = fill_column(model, 0, 1, ["p", "q"])
    values = get_all_values(model, 0)
    assert len(values) == 4
