"""Tests for sylk_parser.write_sylk — mainstream-product-deepening-rnext7.

Covers: write then parse roundtrip, numeric cells, string cells, empty doc, file creation.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    write_sylk,
    parse_sylk_strict,
    SylkError,
)


def _make_doc(*cells_data) -> SylkDocument:
    cells = [SylkCell(row=r, col=c, value=v, value_type=t) for r, c, v, t in cells_data]
    max_row = max(c.row for c in cells) if cells else 0
    max_col = max(c.col for c in cells) if cells else 0
    return SylkDocument(cells=cells, rows=max_row, cols=max_col)


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------

def test_write_sylk_creates_file():
    doc = _make_doc((1, 1, "hello", "string"))
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False) as f:
        path = Path(f.name)
    write_sylk(doc, path)
    assert path.exists()
    assert path.stat().st_size > 0


def test_write_sylk_roundtrip_string():
    doc = _make_doc((1, 1, "test_value", "string"))
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False) as f:
        path = Path(f.name)
    write_sylk(doc, path)
    result = parse_sylk_strict(path)
    assert result.cells[0].value == "test_value"


def test_write_sylk_roundtrip_numeric():
    doc = _make_doc((1, 1, 42, "numeric"))
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False) as f:
        path = Path(f.name)
    write_sylk(doc, path)
    result = parse_sylk_strict(path)
    assert result.cells[0].value == 42


def test_write_sylk_multiple_cells():
    doc = _make_doc((1, 1, "A", "string"), (1, 2, "B", "string"), (2, 1, "C", "string"))
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False) as f:
        path = Path(f.name)
    write_sylk(doc, path)
    result = parse_sylk_strict(path)
    assert len(result.cells) == 3


def test_write_sylk_file_has_id_header():
    doc = _make_doc((1, 1, "x", "string"))
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False) as f:
        path = Path(f.name)
    write_sylk(doc, path)
    content = path.read_text()
    assert content.startswith("ID;P")


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

def test_write_sylk_empty_doc():
    doc = SylkDocument(cells=[], rows=0, cols=0)
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False) as f:
        path = Path(f.name)
    write_sylk(doc, path)
    assert path.exists()


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

def test_write_sylk_invalid_path_raises():
    doc = _make_doc((1, 1, "x", "string"))
    with pytest.raises(SylkError):
        write_sylk(doc, "/nonexistent/path/file.slk")
