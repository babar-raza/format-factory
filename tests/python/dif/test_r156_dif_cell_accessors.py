"""
test_r156_dif_cell_accessors.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT14-001
Added: 2026-06-10

Tests for DIF get_cell_value, set_cell_value, get_row_values functions.
Authority: P5 (SAL-DIF-00001)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    get_cell_value,
    set_cell_value,
    get_row_values,
    write_dif,
    DifCell,
    DifDocument,
    DifError,
)


def _make_dif(tmp_path: Path, title: str, rows: list[list[tuple]]) -> Path:
    """Create a DIF file from row data. Each tuple is (value, value_type)."""
    doc = DifDocument(title=title)
    for row_data in rows:
        row = [DifCell(value=v, value_type=t) for v, t in row_data]
        doc.rows.append(row)
    doc.vectors = max((len(r) for r in doc.rows), default=0)
    doc.tuples = len(doc.rows)
    p = tmp_path / "test.dif"
    write_dif(doc, p)
    return p


# ---- get_cell_value tests ----


class TestGetCellValue:
    def test_numeric_cell(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(42.0, "numeric"), ("hello", "string")]])
        assert get_cell_value(src, 0, 0) == 42.0

    def test_string_cell(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(42.0, "numeric"), ("hello", "string")]])
        assert get_cell_value(src, 0, 1) == "hello"

    def test_out_of_range_row(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        assert get_cell_value(src, 5, 0) is None

    def test_out_of_range_col(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        assert get_cell_value(src, 0, 5) is None

    def test_negative_index(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        assert get_cell_value(src, -1, 0) is None

    def test_multiple_rows(self, tmp_path):
        src = _make_dif(tmp_path, "Multi", [
            [(10.0, "numeric"), (20.0, "numeric")],
            [(30.0, "numeric"), (40.0, "numeric")],
        ])
        assert get_cell_value(src, 1, 1) == 40.0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            get_cell_value(tmp_path / "ghost.dif", 0, 0)


# ---- set_cell_value tests ----


class TestSetCellValue:
    def test_set_numeric(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric"), (2.0, "numeric")]])
        dst = tmp_path / "out.dif"
        result = set_cell_value(src, dst, 0, 0, 99.0, "numeric")
        assert result["ok"] is True
        assert result["old_value"] == 1.0
        assert result["new_value"] == 99.0
        assert get_cell_value(dst, 0, 0) == 99.0

    def test_set_string(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric"), ("old", "string")]])
        dst = tmp_path / "out.dif"
        set_cell_value(src, dst, 0, 1, "new", "string")
        assert get_cell_value(dst, 0, 1) == "new"

    def test_preserves_other_cells(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [
            [(10.0, "numeric"), (20.0, "numeric")],
            [(30.0, "numeric"), (40.0, "numeric")],
        ])
        dst = tmp_path / "out.dif"
        set_cell_value(src, dst, 0, 0, 99.0, "numeric")
        assert get_cell_value(dst, 1, 1) == 40.0

    def test_row_out_of_range(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        dst = tmp_path / "out.dif"
        with pytest.raises(DifError):
            set_cell_value(src, dst, 5, 0, 1.0, "numeric")

    def test_col_out_of_range(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        dst = tmp_path / "out.dif"
        with pytest.raises(DifError):
            set_cell_value(src, dst, 0, 5, 1.0, "numeric")

    def test_result_keys(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        dst = tmp_path / "out.dif"
        result = set_cell_value(src, dst, 0, 0, 2.0, "numeric")
        assert "ok" in result
        assert "row" in result
        assert "col" in result
        assert "old_value" in result
        assert "new_value" in result


# ---- get_row_values tests ----


class TestGetRowValues:
    def test_single_row(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(10.0, "numeric"), ("abc", "string")]])
        vals = get_row_values(src, 0)
        assert vals == [10.0, "abc"]

    def test_second_row(self, tmp_path):
        src = _make_dif(tmp_path, "Multi", [
            [(1.0, "numeric")],
            [(2.0, "numeric"), (3.0, "numeric")],
        ])
        vals = get_row_values(src, 1)
        assert vals == [2.0, 3.0]

    def test_out_of_range(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        assert get_row_values(src, 10) == []

    def test_negative_index(self, tmp_path):
        src = _make_dif(tmp_path, "Test", [[(1.0, "numeric")]])
        assert get_row_values(src, -1) == []

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            get_row_values(tmp_path / "ghost.dif", 0)

    def test_empty_document(self, tmp_path):
        src = _make_dif(tmp_path, "Empty", [])
        assert get_row_values(src, 0) == []
