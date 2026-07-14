"""Roundtrip tests for sylk_writer.py — TC-W4-004."""
from __future__ import annotations

import pytest
from pathlib import Path
from sylk.sylk_writer import write_sylk, write_sylk_str, SylkWriteError
from sylk.sylk_parser import parse_sylk_strict


def test_write_sylk_str_has_header_and_terminator():
    class FakeDoc:
        cells = []
    out = write_sylk_str(FakeDoc())
    assert out.startswith("ID;P")
    assert out.strip().endswith("E")


def test_write_sylk_str_cell_record():
    class FakeCell:
        row = 1
        col = 2
        value = "Hello"
    class FakeDoc:
        cells = [FakeCell()]
    out = write_sylk_str(FakeDoc())
    assert 'C;X2;Y1;K"Hello"' in out


def test_write_sylk_numeric_cell():
    class FakeCell:
        row = 1
        col = 1
        value = 42
    class FakeDoc:
        cells = [FakeCell()]
    out = write_sylk_str(FakeDoc())
    assert "C;X1;Y1;K42" in out


def test_write_sylk_roundtrip(tmp_path):
    doc = parse_sylk_strict("samples/by-format/sylk/valid/minimal-2x2.slk")
    out_path = tmp_path / "out.slk"
    write_sylk(doc, out_path)
    re_parsed = parse_sylk_strict(str(out_path))
    assert re_parsed.rows == doc.rows
    assert re_parsed.cols == doc.cols
    orig_vals = {(c.row, c.col): c.value for c in doc.cells}
    new_vals = {(c.row, c.col): c.value for c in re_parsed.cells}
    for pos, val in orig_vals.items():
        assert new_vals.get(pos) == val, f"Cell {pos}: expected {val}, got {new_vals.get(pos)}"


def test_write_sylk_none_document_raises():
    with pytest.raises(SylkWriteError):
        write_sylk_str(None)
