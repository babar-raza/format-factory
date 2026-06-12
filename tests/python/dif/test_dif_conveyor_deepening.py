"""
test_dif_conveyor_deepening.py -- DIF product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-4
Tests mutation, analytics, and export functions for DIF.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"

from dif.dif_parser import (
    parse_dif,
    parse_dif_strict,
    write_dif,
    dif_to_csv,
    count_nonempty_cells,
    total_cell_count,
    get_all_values,
    min_column_value,
    max_column_value,
    add_row,
    delete_row,
)


def test_add_row_to_doc(tmp_path):
    doc = parse_dif_strict(str(_SAMPLES / "minimal-2x2.dif"))
    original_rows = len(doc.rows)
    result = add_row(doc, [99, "added"])
    assert result["success"] is True
    assert len(doc.rows) == original_rows + 1
    out = tmp_path / "added.dif"
    write_dif(doc, str(out))
    reparsed = parse_dif(str(out))
    assert reparsed["ok"] is True


def test_delete_row_from_doc(tmp_path):
    doc = parse_dif_strict(str(_SAMPLES / "minimal-2x2.dif"))
    original_rows = len(doc.rows)
    result = delete_row(doc, 1)
    assert result["success"] is True
    assert len(doc.rows) == original_rows - 1


def test_min_column_value():
    val = min_column_value(str(_SAMPLES / "numeric-row.dif"), 0)
    assert val is not None
    assert isinstance(val, (int, float))


def test_max_column_value():
    val = max_column_value(str(_SAMPLES / "numeric-row.dif"), 0)
    assert val is not None
    assert isinstance(val, (int, float))


def test_min_max_relationship():
    lo = min_column_value(str(_SAMPLES / "numeric-row.dif"), 0)
    hi = max_column_value(str(_SAMPLES / "numeric-row.dif"), 0)
    if lo is not None and hi is not None:
        assert lo <= hi


def test_total_cell_count():
    count = total_cell_count(str(_SAMPLES / "minimal-2x2.dif"))
    assert isinstance(count, int)
    assert count >= 4


def test_count_nonempty_cells():
    count = count_nonempty_cells(str(_SAMPLES / "minimal-2x2.dif"))
    assert isinstance(count, int)
    assert count >= 1


def test_dif_to_csv_export():
    csv_text = dif_to_csv(str(_SAMPLES / "minimal-2x2.dif"))
    assert isinstance(csv_text, str)
    assert len(csv_text) > 0
    # CSV may use \r\n or \n depending on platform; just check non-empty
    lines = [l for l in csv_text.splitlines() if l.strip()]
    assert len(lines) >= 1


def test_get_all_values():
    vals = get_all_values(str(_SAMPLES / "minimal-2x2.dif"))
    assert isinstance(vals, list)
    assert len(vals) >= 4


def test_write_and_reparse(tmp_path):
    doc = parse_dif_strict(str(_SAMPLES / "minimal-2x2.dif"))
    out = tmp_path / "rewrite.dif"
    write_dif(doc, str(out))
    reparsed = parse_dif(str(out))
    assert reparsed["ok"] is True
