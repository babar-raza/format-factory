"""R563: SYLK cell type properties — numeric_cell_count, string_cell_count, nonempty_cell_count.

Tests for SylkModelDocument cell type properties added in R563.
Spec refs: FACT-SYLK-008 (numeric values), FACT-SYLK-016 (string values).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.models import SylkModelDocument, SylkDoc

SAMPLES = Path("samples/by-format/sylk/valid")


def _make_cell(value_type, value=None, row=1, col=1):
    return types.SimpleNamespace(value=value, value_type=value_type, row=row, col=col)


def _make_doc(cells=None, rows=1, cols=1):
    """Build a minimal SylkModelDocument."""
    if cells is None:
        cells = []
    return SylkModelDocument(types.SimpleNamespace(
        rows=rows, cols=cols, cells=cells, path="test.slk", id_line="ID;P"
    ))


class TestNumericCellCount:
    def test_no_numeric_cells(self):
        doc = _make_doc(cells=[_make_cell("string", "hello")])
        assert doc.numeric_cell_count == 0

    def test_one_numeric_cell(self):
        doc = _make_doc(cells=[_make_cell("numeric", 42.0)])
        assert doc.numeric_cell_count == 1

    def test_multiple_numeric_cells(self):
        cells = [_make_cell("numeric", float(i), row=i, col=1) for i in range(1, 4)]
        doc = _make_doc(cells=cells, rows=3, cols=1)
        assert doc.numeric_cell_count == 3

    def test_mixed_cells(self):
        cells = [
            _make_cell("numeric", 1.0, row=1, col=1),
            _make_cell("string", "text", row=1, col=2),
            _make_cell("empty", None, row=2, col=1),
        ]
        doc = _make_doc(cells=cells, rows=2, cols=2)
        assert doc.numeric_cell_count == 1

    def test_numeric_cell_count_type(self):
        doc = _make_doc(cells=[])
        assert isinstance(doc.numeric_cell_count, int)

    def test_empty_doc_zero_numeric(self):
        doc = _make_doc(cells=[])
        assert doc.numeric_cell_count == 0


class TestStringCellCount:
    def test_no_string_cells(self):
        doc = _make_doc(cells=[_make_cell("numeric", 5.0)])
        assert doc.string_cell_count == 0

    def test_one_string_cell(self):
        doc = _make_doc(cells=[_make_cell("string", "hello")])
        assert doc.string_cell_count == 1

    def test_multiple_string_cells(self):
        cells = [_make_cell("string", f"s{i}", row=i, col=1) for i in range(1, 5)]
        doc = _make_doc(cells=cells, rows=4, cols=1)
        assert doc.string_cell_count == 4

    def test_string_cell_count_type(self):
        doc = _make_doc(cells=[])
        assert isinstance(doc.string_cell_count, int)

    def test_empty_only_cells_no_strings(self):
        cells = [_make_cell("empty", None, row=i, col=1) for i in range(1, 3)]
        doc = _make_doc(cells=cells)
        assert doc.string_cell_count == 0


class TestNonemptyCellCount:
    def test_all_empty_zero_nonempty(self):
        cells = [_make_cell("empty", None, row=i, col=1) for i in range(1, 4)]
        doc = _make_doc(cells=cells, rows=3)
        assert doc.nonempty_cell_count == 0

    def test_all_numeric_all_nonempty(self):
        cells = [_make_cell("numeric", float(i), row=i, col=1) for i in range(1, 4)]
        doc = _make_doc(cells=cells, rows=3)
        assert doc.nonempty_cell_count == 3

    def test_mixed_nonempty_count(self):
        cells = [
            _make_cell("numeric", 1.0, row=1, col=1),
            _make_cell("string", "hi", row=1, col=2),
            _make_cell("empty", None, row=2, col=1),
            _make_cell("empty", None, row=2, col=2),
        ]
        doc = _make_doc(cells=cells, rows=2, cols=2)
        assert doc.nonempty_cell_count == 2

    def test_nonempty_cell_count_type(self):
        doc = _make_doc(cells=[])
        assert isinstance(doc.nonempty_cell_count, int)

    def test_nonempty_equals_numeric_plus_string(self):
        cells = [
            _make_cell("numeric", 99.9, row=1, col=1),
            _make_cell("string", "abc", row=1, col=2),
            _make_cell("empty", None, row=2, col=1),
        ]
        doc = _make_doc(cells=cells, rows=2, cols=2)
        assert doc.nonempty_cell_count == doc.numeric_cell_count + doc.string_cell_count


class TestCellTypeConsistency:
    def test_alias_has_properties(self):
        doc = _make_doc(cells=[_make_cell("numeric", 1.0)])
        assert isinstance(doc, SylkDoc)
        assert hasattr(doc, "numeric_cell_count")
        assert hasattr(doc, "string_cell_count")
        assert hasattr(doc, "nonempty_cell_count")

    def test_from_file(self):
        doc = SylkModelDocument.from_file(SAMPLES / "numeric-row.slk")
        assert isinstance(doc.numeric_cell_count, int)
        assert isinstance(doc.string_cell_count, int)
        assert isinstance(doc.nonempty_cell_count, int)
        assert doc.nonempty_cell_count == doc.numeric_cell_count + doc.string_cell_count
