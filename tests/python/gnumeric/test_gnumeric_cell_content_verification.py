"""
test_gnumeric_cell_content_verification.py -- Gnumeric cell content verification.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-12
Tests get_cell_value, get_row, get_column with exact content assertions
from real sample files. Addresses W9-GNUMERIC-GAP-CLOSURE advisory.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import (
    load,
    get_cell_value,
    get_row,
    get_column,
    get_row_count,
    get_column_count,
    extract_values,
)


def test_minimal_cell_value_is_hello():
    m = load(str(_SAMPLES / "minimal-spreadsheet.gnumeric"))
    assert get_cell_value(m, 0, 0, 0) == "Hello"


def test_multi_cell_header_row_content():
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    row0 = get_row(m, 0, 0)
    assert row0[0] == "Name"
    assert row0[1] == "Score"


def test_multi_cell_data_row_content():
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    row1 = get_row(m, 0, 1)
    assert row1[0] == "Alice"
    assert row1[1] == "42"


def test_multi_cell_column_zero_content():
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    col0 = get_column(m, 0, 0)
    assert "Name" in col0
    assert "Alice" in col0


def test_multi_cell_row_count_is_two():
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    assert get_row_count(m, 0) == 2


def test_multi_cell_column_count_is_two():
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    assert get_column_count(m, 0) == 2


def test_extract_values_contains_known_strings():
    values = extract_values(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    assert "Name" in values
    assert "Alice" in values
    assert "42" in values
