"""
test_r158_dif_all_values.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT18-001
Added: 2026-06-10

Tests for DIF get_all_values function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import get_all_values, write_dif, DifCell, DifDocument, DifError


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


class TestGetAllValues:
    def test_single_row(self, tmp_path):
        src = _make_dif(tmp_path, [[(1.0, "numeric"), (2.0, "numeric")]])
        vals = get_all_values(src)
        assert vals == [1.0, 2.0]

    def test_multiple_rows(self, tmp_path):
        src = _make_dif(tmp_path, [
            [(1.0, "numeric"), (2.0, "numeric")],
            [(3.0, "numeric"), (4.0, "numeric")],
        ])
        vals = get_all_values(src)
        assert vals == [1.0, 2.0, 3.0, 4.0]

    def test_mixed_types(self, tmp_path):
        src = _make_dif(tmp_path, [
            [("hello", "string"), (42.0, "numeric")],
        ])
        vals = get_all_values(src)
        assert vals == ["hello", 42.0]

    def test_empty_document(self, tmp_path):
        src = _make_dif(tmp_path, [])
        vals = get_all_values(src)
        assert vals == []

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            get_all_values(tmp_path / "ghost.dif")

    def test_returns_list(self, tmp_path):
        src = _make_dif(tmp_path, [[(1.0, "numeric")]])
        vals = get_all_values(src)
        assert isinstance(vals, list)
