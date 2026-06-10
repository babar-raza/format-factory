"""
test_r156_dif_column_values.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT15-001
Added: 2026-06-10

Tests for DIF get_column_values function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    get_column_values,
    write_dif,
    DifCell,
    DifDocument,
    DifError,
)


def _make_dif(tmp_path: Path, rows: list[list[tuple]]) -> Path:
    doc = DifDocument(title="Test")
    for row_data in rows:
        row = [DifCell(value=v, value_type=t) for v, t in row_data]
        doc.rows.append(row)
    doc.vectors = max((len(r) for r in doc.rows), default=0)
    doc.tuples = len(doc.rows)
    p = tmp_path / "test.dif"
    write_dif(doc, p)
    return p


class TestGetColumnValues:
    def test_first_column(self, tmp_path):
        src = _make_dif(tmp_path, [
            [(1.0, "numeric"), (10.0, "numeric")],
            [(2.0, "numeric"), (20.0, "numeric")],
            [(3.0, "numeric"), (30.0, "numeric")],
        ])
        vals = get_column_values(src, 0)
        assert vals == [1.0, 2.0, 3.0]

    def test_second_column(self, tmp_path):
        src = _make_dif(tmp_path, [
            [(1.0, "numeric"), (10.0, "numeric")],
            [(2.0, "numeric"), (20.0, "numeric")],
        ])
        vals = get_column_values(src, 1)
        assert vals == [10.0, 20.0]

    def test_string_column(self, tmp_path):
        src = _make_dif(tmp_path, [
            [("a", "string"), (1.0, "numeric")],
            [("b", "string"), (2.0, "numeric")],
        ])
        vals = get_column_values(src, 0)
        assert vals == ["a", "b"]

    def test_out_of_range_column(self, tmp_path):
        src = _make_dif(tmp_path, [
            [(1.0, "numeric")],
            [(2.0, "numeric")],
        ])
        vals = get_column_values(src, 5)
        assert vals == [None, None]

    def test_empty_document(self, tmp_path):
        src = _make_dif(tmp_path, [])
        vals = get_column_values(src, 0)
        assert vals == []

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            get_column_values(tmp_path / "ghost.dif", 0)

    def test_single_row(self, tmp_path):
        src = _make_dif(tmp_path, [[(42.0, "numeric"), ("hello", "string")]])
        vals = get_column_values(src, 0)
        assert vals == [42.0]
