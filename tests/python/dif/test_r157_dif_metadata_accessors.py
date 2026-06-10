"""
test_r157_dif_metadata_accessors.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT16-001
Added: 2026-06-10

Tests for DIF get_title, get_row_count, get_column_count functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    get_title,
    get_row_count,
    get_column_count,
    write_dif,
    DifCell,
    DifDocument,
    DifError,
)


def _make_dif(tmp_path: Path, title: str, rows: list[list[tuple]], vectors: int = 0) -> Path:
    doc = DifDocument(title=title)
    for row_data in rows:
        row = [DifCell(value=v, value_type=t) for v, t in row_data]
        doc.rows.append(row)
    doc.vectors = vectors or max((len(r) for r in doc.rows), default=0)
    doc.tuples = len(doc.rows)
    p = tmp_path / "test.dif"
    write_dif(doc, p)
    return p


class TestGetTitle:
    def test_with_title(self, tmp_path):
        src = _make_dif(tmp_path, "My Report", [[(1.0, "numeric")]])
        assert get_title(src) == "My Report"

    def test_empty_title(self, tmp_path):
        src = _make_dif(tmp_path, "", [[(1.0, "numeric")]])
        assert get_title(src) == ""

    def test_special_chars(self, tmp_path):
        src = _make_dif(tmp_path, "Sheet A & B", [[(1.0, "numeric")]])
        assert get_title(src) == "Sheet A & B"

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            get_title(tmp_path / "ghost.dif")


class TestGetRowCount:
    def test_single_row(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        assert get_row_count(src) == 1

    def test_multiple_rows(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [
            [(1.0, "numeric")],
            [(2.0, "numeric")],
            [(3.0, "numeric")],
        ])
        assert get_row_count(src) == 3

    def test_empty_document(self, tmp_path):
        src = _make_dif(tmp_path, "Empty", [])
        assert get_row_count(src) == 0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            get_row_count(tmp_path / "ghost.dif")


class TestGetColumnCount:
    def test_single_column(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]], vectors=1)
        assert get_column_count(src) == 1

    def test_multiple_columns(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [
            [(1.0, "numeric"), (2.0, "numeric"), (3.0, "numeric")],
        ], vectors=3)
        assert get_column_count(src) == 3

    def test_empty_document(self, tmp_path):
        src = _make_dif(tmp_path, "Empty", [], vectors=0)
        assert get_column_count(src) == 0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            get_column_count(tmp_path / "ghost.dif")
