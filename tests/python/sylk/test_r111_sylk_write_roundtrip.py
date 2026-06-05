# R111 Wave 6: SYLK write→parse roundtrip tests
# Tests write_sylk + parse_sylk cycle

import pytest
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src/python"))

from sylk.sylk_parser import parse_sylk_strict, write_sylk, parse_sylk, sylk_to_csv, SylkDocument, SylkCell


def _make_doc(cells, id_line="ID;P"):
    doc = SylkDocument()
    doc.id_line = id_line
    doc.cells = cells
    return doc


def test_write_parse_roundtrip_basic():
    cells = [SylkCell(row=1, col=1, value="Hello"), SylkCell(row=1, col=2, value="World")]
    doc = _make_doc(cells)
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        result = parse_sylk(path)
        assert result["ok"] is True
        assert result["cell_count"] >= 2
    finally:
        os.unlink(path)


def test_write_parse_numeric_values():
    cells = [SylkCell(row=1, col=1, value="42"), SylkCell(row=2, col=1, value="3.14")]
    doc = _make_doc(cells)
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        result = parse_sylk(path)
        assert result["ok"] is True
    finally:
        os.unlink(path)


def test_write_parse_empty_document():
    doc = _make_doc([])
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        result = parse_sylk(path)
        assert result["ok"] is True
    finally:
        os.unlink(path)


def test_write_parse_single_cell():
    cells = [SylkCell(row=1, col=1, value="onlycell")]
    doc = _make_doc(cells)
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        result = parse_sylk(path)
        assert result["ok"] is True
        assert result["cell_count"] >= 1
    finally:
        os.unlink(path)


def test_write_csv_export_roundtrip():
    cells = [SylkCell(row=1, col=1, value="A"), SylkCell(row=1, col=2, value="B"),
             SylkCell(row=2, col=1, value="C"), SylkCell(row=2, col=2, value="D")]
    doc = _make_doc(cells)
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        csv_text = sylk_to_csv(path)
        assert "A" in csv_text
        assert "D" in csv_text
    finally:
        os.unlink(path)


def test_write_parse_strict_roundtrip():
    cells = [SylkCell(row=1, col=1, value="strict_test")]
    doc = _make_doc(cells)
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        result = parse_sylk_strict(path)
        assert hasattr(result, "cells")
        assert len(result.cells) >= 1
    finally:
        os.unlink(path)


def test_write_parse_multi_row():
    cells = [SylkCell(row=r, col=1, value=f"row{r}") for r in range(1, 11)]
    doc = _make_doc(cells)
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        result = parse_sylk(path)
        assert result["ok"] is True
        assert result["cell_count"] >= 10
    finally:
        os.unlink(path)


def test_write_parse_preserves_id_line():
    cells = [SylkCell(row=1, col=1, value="x")]
    doc = _make_doc(cells, id_line="ID;P")
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w") as f:
        path = f.name
    try:
        write_sylk(doc, path)
        result = parse_sylk(path)
        assert result["ok"] is True
        assert "ID" in result.get("id_line", "ID")
    finally:
        os.unlink(path)
