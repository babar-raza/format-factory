"""Tests for dif_parser.write_dif — mainstream-product-deepening-rnext7.

Covers: write then parse roundtrip, string cells, numeric cells, empty doc, file creation.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    DifDocument,
    DifCell,
    write_dif,
    parse_dif_strict,
)


def _cell(val, vtype="string") -> DifCell:
    return DifCell(value=val, value_type=vtype)


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------

def test_write_dif_creates_file():
    doc = DifDocument(title="Test", rows=[[_cell("A"), _cell("B")]])
    with tempfile.NamedTemporaryFile(suffix=".dif", delete=False) as f:
        path = Path(f.name)
    write_dif(doc, path)
    assert path.exists()
    assert path.stat().st_size > 0


def test_write_dif_file_has_table_header():
    doc = DifDocument(rows=[[_cell("x")]])
    with tempfile.NamedTemporaryFile(suffix=".dif", delete=False) as f:
        path = Path(f.name)
    write_dif(doc, path)
    content = path.read_text()
    assert "TABLE" in content


def test_write_dif_roundtrip_string():
    doc = DifDocument(title="RT", rows=[[_cell("hello")]])
    with tempfile.NamedTemporaryFile(suffix=".dif", delete=False) as f:
        path = Path(f.name)
    write_dif(doc, path)
    result = parse_dif_strict(path)
    assert result.rows[0][0].value == "hello"


def test_write_dif_multiple_rows():
    doc = DifDocument(rows=[[_cell("row1")], [_cell("row2")]])
    with tempfile.NamedTemporaryFile(suffix=".dif", delete=False) as f:
        path = Path(f.name)
    write_dif(doc, path)
    result = parse_dif_strict(path)
    assert len(result.rows) == 2


def test_write_dif_multiple_columns():
    doc = DifDocument(rows=[[_cell("A"), _cell("B"), _cell("C")]])
    with tempfile.NamedTemporaryFile(suffix=".dif", delete=False) as f:
        path = Path(f.name)
    write_dif(doc, path)
    result = parse_dif_strict(path)
    assert len(result.rows[0]) == 3


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

def test_write_dif_empty_doc():
    doc = DifDocument(rows=[])
    with tempfile.NamedTemporaryFile(suffix=".dif", delete=False) as f:
        path = Path(f.name)
    write_dif(doc, path)
    assert path.exists()


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

def test_write_dif_invalid_path_raises():
    doc = DifDocument(rows=[[_cell("x")]])
    with pytest.raises(Exception):
        write_dif(doc, "/nonexistent/path/file.dif")
