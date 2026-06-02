# R93 Train P: SYLK write round-trip tests
# Governed skill: /add-python-object-model-feature
# Ledger: R93-GOVERNED-PYTHON-SYLK-WRITE-001
# Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

from pathlib import Path

import pytest

from sylk.sylk_parser import (
    SylkCell,
    SylkDocument,
    SylkError,
    parse_sylk_strict,
    write_sylk,
)


def make_doc(*cells: SylkCell) -> SylkDocument:
    rows = max((c.row for c in cells), default=0)
    cols = max((c.col for c in cells), default=0)
    return SylkDocument(cells=list(cells), rows=rows, cols=cols)


def test_write_creates_file(tmp_path: Path):
    doc = make_doc(SylkCell(row=1, col=1, value=42, value_type="numeric"))
    out = tmp_path / "out.slk"
    write_sylk(doc, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_write_read_numeric_roundtrip(tmp_path: Path):
    doc = make_doc(
        SylkCell(row=1, col=1, value=10, value_type="numeric"),
        SylkCell(row=1, col=2, value=20, value_type="numeric"),
    )
    out = tmp_path / "num.slk"
    write_sylk(doc, out)
    loaded = parse_sylk_strict(out)
    values = {(c.row, c.col): c.value for c in loaded.cells}
    assert values[(1, 1)] == 10
    assert values[(1, 2)] == 20


def test_write_read_string_roundtrip(tmp_path: Path):
    doc = make_doc(
        SylkCell(row=1, col=1, value="Hello", value_type="string"),
        SylkCell(row=2, col=1, value="World", value_type="string"),
    )
    out = tmp_path / "str.slk"
    write_sylk(doc, out)
    loaded = parse_sylk_strict(out)
    values = {(c.row, c.col): c.value for c in loaded.cells}
    assert values[(1, 1)] == "Hello"
    assert values[(2, 1)] == "World"


def test_write_empty_doc_produces_valid_sylk(tmp_path: Path):
    doc = SylkDocument(cells=[], rows=0, cols=0)
    out = tmp_path / "empty.slk"
    write_sylk(doc, out)
    content = out.read_text(encoding="ascii")
    assert content.startswith("ID;P")
    assert content.strip().endswith("E")


def test_write_file_starts_with_id_record(tmp_path: Path):
    doc = make_doc(SylkCell(row=1, col=1, value=1, value_type="numeric"))
    out = tmp_path / "id.slk"
    write_sylk(doc, out)
    content = out.read_text(encoding="ascii")
    assert content.startswith("ID;P")


def test_write_skip_none_value_cells(tmp_path: Path):
    """Cells with value=None are omitted from the output."""
    doc = make_doc(
        SylkCell(row=1, col=1, value=None, value_type="empty"),
        SylkCell(row=1, col=2, value=99, value_type="numeric"),
    )
    out = tmp_path / "none.slk"
    write_sylk(doc, out)
    loaded = parse_sylk_strict(out)
    assert len(loaded.cells) == 1
    assert loaded.cells[0].value == 99


def test_write_mixed_types_roundtrip(tmp_path: Path):
    doc = make_doc(
        SylkCell(row=1, col=1, value="Name", value_type="string"),
        SylkCell(row=1, col=2, value="Score", value_type="string"),
        SylkCell(row=2, col=1, value="Alice", value_type="string"),
        SylkCell(row=2, col=2, value=98.5, value_type="numeric"),
    )
    out = tmp_path / "mixed.slk"
    write_sylk(doc, out)
    loaded = parse_sylk_strict(out)
    values = {(c.row, c.col): c.value for c in loaded.cells}
    assert values[(1, 1)] == "Name"
    assert values[(2, 1)] == "Alice"
    assert abs(values[(2, 2)] - 98.5) < 0.001


def test_write_float_value_roundtrip(tmp_path: Path):
    doc = make_doc(SylkCell(row=1, col=1, value=3.14159, value_type="numeric"))
    out = tmp_path / "float.slk"
    write_sylk(doc, out)
    loaded = parse_sylk_strict(out)
    assert abs(loaded.cells[0].value - 3.14159) < 0.00001
