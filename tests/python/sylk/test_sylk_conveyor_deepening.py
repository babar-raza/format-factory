"""
test_sylk_conveyor_deepening.py -- SYLK product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-4
Tests mutation, analytics, and export functions for SYLK.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"

from sylk.sylk_parser import (
    parse_sylk,
    parse_sylk_strict,
    write_sylk,
    sylk_to_csv,
    sylk_to_html,
    get_cell_value,
    get_column_values,
    get_all_values,
    set_cell_value,
    add_row,
    delete_row,
    count_nonempty_cells,
    sum_column,
)


def test_add_row_and_reparse(tmp_path):
    src = _SAMPLES / "minimal-2x2.slk"
    dest = tmp_path / "added.slk"
    result = add_row(str(src), str(dest), [42, "hello"])
    assert result["success"] is True
    assert result["row_index"] >= 1
    reparsed = parse_sylk(str(dest))
    assert reparsed["ok"] is True


def test_delete_row_and_reparse(tmp_path):
    src = _SAMPLES / "minimal-2x2.slk"
    dest = tmp_path / "deleted.slk"
    result = delete_row(str(src), str(dest), 1)
    assert result["success"] is True
    reparsed = parse_sylk(str(dest))
    assert reparsed["ok"] is True


def test_set_cell_value_roundtrip(tmp_path):
    src = _SAMPLES / "minimal-2x2.slk"
    dest = tmp_path / "modified.slk"
    result = set_cell_value(str(src), str(dest), 1, 1, "new_val", "string")
    assert result["ok"] is True
    assert result["new_value"] == "new_val"
    val = get_cell_value(str(dest), 1, 1)
    assert val == "new_val"


def test_sylk_to_csv_export():
    csv_text = sylk_to_csv(str(_SAMPLES / "minimal-2x2.slk"))
    assert isinstance(csv_text, str)
    assert len(csv_text) > 0
    lines = csv_text.strip().split("\r\n")
    assert len(lines) >= 2


def test_sylk_to_html_export():
    html = sylk_to_html(str(_SAMPLES / "minimal-2x2.slk"))
    assert "<table>" in html
    assert "<td>" in html
    assert "</table>" in html


def test_count_nonempty_cells():
    count = count_nonempty_cells(str(_SAMPLES / "minimal-2x2.slk"))
    assert isinstance(count, int)
    assert count >= 1


def test_sum_column_numeric():
    total = sum_column(str(_SAMPLES / "numeric-row.slk"), 1)
    assert isinstance(total, float)


def test_get_column_values():
    vals = get_column_values(str(_SAMPLES / "minimal-2x2.slk"), 1)
    assert isinstance(vals, list)
    assert len(vals) >= 1


def test_get_all_values():
    vals = get_all_values(str(_SAMPLES / "minimal-2x2.slk"))
    assert isinstance(vals, list)
    assert len(vals) >= 1


def test_write_and_reparse(tmp_path):
    doc = parse_sylk_strict(str(_SAMPLES / "minimal-2x2.slk"))
    out = tmp_path / "rewrite.slk"
    write_sylk(doc, str(out))
    reparsed = parse_sylk(str(out))
    assert reparsed["ok"] is True
