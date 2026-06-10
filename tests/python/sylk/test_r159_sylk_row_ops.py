"""Tests for SYLK add_row and delete_row.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT19-001
Covers: add_row, delete_row with roundtrip verification
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import (
    parse_sylk_strict,
    write_sylk,
    add_row,
    delete_row,
    get_row_count,
    get_cell_value,
    SylkDocument,
    SylkCell,
)


def _make_sylk_file():
    """Create a minimal SYLK file with 2 rows."""
    doc = SylkDocument(cells=[
        SylkCell(row=1, col=1, value="Name", value_type="string"),
        SylkCell(row=1, col=2, value="Age", value_type="string"),
        SylkCell(row=2, col=1, value="Alice", value_type="string"),
        SylkCell(row=2, col=2, value=30, value_type="numeric"),
    ])
    path = Path(tempfile.mktemp(suffix=".sylk"))
    write_sylk(doc, path)
    return path


class TestAddRow:
    def test_add_row_increases_count(self):
        src = _make_sylk_file()
        dst = Path(tempfile.mktemp(suffix=".sylk"))
        try:
            original_count = get_row_count(src)
            result = add_row(src, dst, ["Bob", 25])
            assert result["success"] is True
            new_count = get_row_count(dst)
            assert new_count == original_count + 1
        finally:
            src.unlink(missing_ok=True)
            dst.unlink(missing_ok=True)

    def test_add_row_values_readable(self):
        src = _make_sylk_file()
        dst = Path(tempfile.mktemp(suffix=".sylk"))
        try:
            add_row(src, dst, ["Charlie", 35])
            val = get_cell_value(dst, 3, 1)
            assert val == "Charlie"
        finally:
            src.unlink(missing_ok=True)
            dst.unlink(missing_ok=True)

    def test_add_row_returns_row_index(self):
        src = _make_sylk_file()
        dst = Path(tempfile.mktemp(suffix=".sylk"))
        try:
            result = add_row(src, dst, ["X"])
            assert result["row_index"] == 3
            assert result["cell_count"] == 1
        finally:
            src.unlink(missing_ok=True)
            dst.unlink(missing_ok=True)


class TestDeleteRow:
    def test_delete_row_decreases_count(self):
        src = _make_sylk_file()
        dst = Path(tempfile.mktemp(suffix=".sylk"))
        try:
            original_count = get_row_count(src)
            result = delete_row(src, dst, 2)
            assert result["success"] is True
            new_count = get_row_count(dst)
            assert new_count == original_count - 1
        finally:
            src.unlink(missing_ok=True)
            dst.unlink(missing_ok=True)

    def test_delete_row_preserves_other_rows(self):
        src = _make_sylk_file()
        dst = Path(tempfile.mktemp(suffix=".sylk"))
        try:
            delete_row(src, dst, 2)
            val = get_cell_value(dst, 1, 1)
            assert val == "Name"
        finally:
            src.unlink(missing_ok=True)
            dst.unlink(missing_ok=True)

    def test_delete_returns_count(self):
        src = _make_sylk_file()
        dst = Path(tempfile.mktemp(suffix=".sylk"))
        try:
            result = delete_row(src, dst, 2)
            assert result["deleted_count"] == 2  # 2 cells in row 2
        finally:
            src.unlink(missing_ok=True)
            dst.unlink(missing_ok=True)
