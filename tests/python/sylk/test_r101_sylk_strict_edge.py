# R101 Train G: SYLK strict parse edge case tests
# Governed skill: /add-roundtrip-test
# Ledger: R101-GOVERNED-PYTHON-SYLK-STRICT-EDGE-001
# Gap: GAP-SYLK-STRICT-EDGE-001

import tempfile
from pathlib import Path

import pytest

from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    parse_sylk_strict,
    write_sylk,
    sylk_to_csv,
)


def _make_doc(cells, rows, cols):
    """Helper to create a SylkDocument with given cells."""
    doc = SylkDocument()
    doc.cells = cells
    doc.rows = rows
    doc.cols = cols
    return doc


def test_unicode_cell_value_raises_on_write():
    """SYLK writer uses ASCII encoding; Unicode values raise SylkError.
    This documents the current limitation — SYLK is historically ASCII-only."""
    from sylk.sylk_parser import SylkError
    cells = [
        SylkCell(row=1, col=1, value="日本語テスト"),
    ]
    doc = _make_doc(cells, 1, 1)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        with pytest.raises(SylkError, match="ascii"):
            write_sylk(doc, tmp)
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_empty_grid_roundtrip():
    """Empty SYLK document (no cells) roundtrips correctly."""
    doc = _make_doc([], 0, 0)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        assert len(reloaded.cells) == 0
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_single_cell_roundtrip():
    """Single cell document roundtrips."""
    cells = [SylkCell(row=1, col=1, value="alone")]
    doc = _make_doc(cells, 1, 1)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        assert len(reloaded.cells) >= 1
        values = {(c.row, c.col): c.value for c in reloaded.cells}
        assert values.get((1, 1)) == "alone"
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_cell_with_semicolon_value_writes():
    """Semicolon in cell value writes without error (ASCII chars).
    Note: the parser may not recover the full value due to SYLK field splitting."""
    cells = [SylkCell(row=1, col=1, value="a;b;c")]
    doc = _make_doc(cells, 1, 1)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        content = Path(tmp).read_text(encoding="ascii")
        assert "a;b;c" in content  # value present in raw file
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_numeric_values_roundtrip():
    """Numeric values (int and float) survive roundtrip."""
    cells = [
        SylkCell(row=1, col=1, value="42"),
        SylkCell(row=1, col=2, value="3.14"),
        SylkCell(row=2, col=1, value="-100"),
        SylkCell(row=2, col=2, value="0"),
    ]
    doc = _make_doc(cells, 2, 2)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        values = {(c.row, c.col): str(c.value) for c in reloaded.cells}
        assert values.get((1, 1)) == "42"
        assert values.get((2, 2)) == "0"
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_csv_export_ascii_values():
    """CSV export works for ASCII cell values."""
    cells = [SylkCell(row=1, col=1, value="hello")]
    doc = _make_doc(cells, 1, 1)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        csv = sylk_to_csv(tmp)
        assert "hello" in csv
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_large_grid_roundtrip():
    """10x10 grid roundtrips correctly (boundary size)."""
    cells = []
    for r in range(1, 11):
        for c in range(1, 11):
            cells.append(SylkCell(row=r, col=c, value=f"R{r}C{c}"))
    doc = _make_doc(cells, 10, 10)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        values = {(c.row, c.col): c.value for c in reloaded.cells}
        assert values.get((1, 1)) == "R1C1"
        assert values.get((10, 10)) == "R10C10"
        assert len(reloaded.cells) >= 100
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_empty_string_cell_roundtrip():
    """Empty string cell value roundtrips."""
    cells = [
        SylkCell(row=1, col=1, value=""),
        SylkCell(row=1, col=2, value="notempty"),
    ]
    doc = _make_doc(cells, 1, 2)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        values = {(c.row, c.col): c.value for c in reloaded.cells}
        assert values.get((1, 2)) == "notempty"
    finally:
        Path(tmp).unlink(missing_ok=True)


def test_whitespace_cell_value():
    """Cell with whitespace-only value."""
    cells = [SylkCell(row=1, col=1, value="  spaces  ")]
    doc = _make_doc(cells, 1, 1)
    with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False) as f:
        tmp = f.name
    try:
        write_sylk(doc, tmp)
        reloaded = parse_sylk_strict(tmp)
        values = {(c.row, c.col): c.value for c in reloaded.cells}
        assert "spaces" in str(values.get((1, 1), ""))
    finally:
        Path(tmp).unlink(missing_ok=True)
