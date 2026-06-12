"""
test_gnumeric_column_extraction.py -- Gnumeric column extraction pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-29
Tests get_column, get_column_count, sum_column, fill_column+get_column,
get_sheet_as_rows on a created Gnumeric model.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    get_column,
    get_column_count,
    sum_column,
    fill_column,
    get_sheet_as_rows,
)

_MODEL = create_gnumeric([{
    "name": "Data",
    "rows": [
        ["Name", "Score"],
        ["Alice", "90"],
        ["Bob", "70"],
        ["Carol", "85"],
    ],
}])


def test_get_column_names():
    col = get_column(_MODEL, 0, 0)
    assert col[0] == "Name"


def test_get_column_count():
    assert get_column_count(_MODEL, 0) == 2


def test_sum_column_scores():
    # col 1 = Score; rows 1-3 are numeric; row 0 "Score" is skipped
    total = sum_column(_MODEL, 0, 1)
    assert total == 245.0


def test_fill_column_then_get():
    m2 = fill_column(_MODEL, 0, 1, ["10", "20", "30", "40"])
    col = get_column(m2, 0, 1)
    assert col[0] == "10"
    assert col[2] == "30"


def test_get_sheet_as_rows():
    rows = get_sheet_as_rows(_MODEL, 0)
    assert len(rows) == 4
    assert rows[0][0] == "Name"
