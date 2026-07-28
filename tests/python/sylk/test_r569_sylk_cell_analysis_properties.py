"""R569: SYLK cell analysis properties — has_numeric_cells, has_string_cells, fill_ratio.

Tests for SylkModelDocument cell analysis properties added in R569.
Spec refs: SAL-SYLK-00001.
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.models import SylkModelDocument, SylkDoc

SAMPLES = Path("samples/by-format/sylk/valid")


def _make_cell(value_type: str, value=None):
    return types.SimpleNamespace(value_type=value_type, value=value)


def _make_doc(row_count=0, col_count=0, cells=None):
    """Build a minimal SylkModelDocument from a stub parsed object."""
    if cells is None:
        cells = []
    return SylkModelDocument(types.SimpleNamespace(
        row_count=row_count,
        col_count=col_count,
        cells=cells,
        id_line="ID;PWXL",
        path="test.slk",
    ))


class TestHasNumericCells:
    def test_one_numeric_cell(self):
        doc = _make_doc(cells=[_make_cell("numeric", 42)])
        assert doc.has_numeric_cells is True

    def test_multiple_numeric_cells(self):
        doc = _make_doc(cells=[_make_cell("numeric", 1), _make_cell("numeric", 2)])
        assert doc.has_numeric_cells is True

    def test_no_numeric_cells(self):
        doc = _make_doc(cells=[_make_cell("string", "hello")])
        assert doc.has_numeric_cells is False

    def test_empty_doc_no_numeric(self):
        doc = _make_doc()
        assert doc.has_numeric_cells is False

    def test_has_numeric_cells_type(self):
        doc = _make_doc(cells=[_make_cell("numeric", 0)])
        assert isinstance(doc.has_numeric_cells, bool)


class TestHasStringCells:
    def test_one_string_cell(self):
        doc = _make_doc(cells=[_make_cell("string", "hello")])
        assert doc.has_string_cells is True

    def test_multiple_string_cells(self):
        doc = _make_doc(cells=[_make_cell("string", "a"), _make_cell("string", "b")])
        assert doc.has_string_cells is True

    def test_no_string_cells_numeric_only(self):
        doc = _make_doc(cells=[_make_cell("numeric", 3.14)])
        assert doc.has_string_cells is False

    def test_empty_doc_no_strings(self):
        doc = _make_doc()
        assert doc.has_string_cells is False

    def test_has_string_cells_type(self):
        doc = _make_doc(cells=[_make_cell("string", "x")])
        assert isinstance(doc.has_string_cells, bool)


class TestFillRatio:
    def test_empty_doc_zero_ratio(self):
        doc = _make_doc()
        assert doc.fill_ratio == 0.0

    def test_all_nonempty_ratio_one(self):
        doc = _make_doc(cells=[_make_cell("numeric", 1), _make_cell("string", "a")])
        assert doc.fill_ratio == 1.0

    def test_half_empty(self):
        doc = _make_doc(cells=[_make_cell("numeric", 1), _make_cell("empty")])
        assert doc.fill_ratio == 0.5

    def test_all_empty_ratio_zero(self):
        doc = _make_doc(cells=[_make_cell("empty"), _make_cell("empty")])
        assert doc.fill_ratio == 0.0

    def test_fill_ratio_type(self):
        doc = _make_doc(cells=[_make_cell("numeric", 1)])
        assert isinstance(doc.fill_ratio, float)

    def test_fill_ratio_between_zero_and_one(self):
        for n_numeric in range(5):
            for n_empty in range(5):
                cells = [_make_cell("numeric")] * n_numeric + [_make_cell("empty")] * n_empty
                doc = _make_doc(cells=cells)
                assert 0.0 <= doc.fill_ratio <= 1.0


class TestCellAnalysisConsistency:
    def test_has_numeric_consistent_with_count(self):
        doc = _make_doc(cells=[_make_cell("numeric", 5)])
        assert doc.has_numeric_cells
        assert doc.numeric_cell_count == 1

    def test_has_string_consistent_with_count(self):
        doc = _make_doc(cells=[_make_cell("string", "x")])
        assert doc.has_string_cells
        assert doc.string_cell_count == 1

    def test_fill_ratio_consistent_with_counts(self):
        cells = [_make_cell("numeric"), _make_cell("string"), _make_cell("empty")]
        doc = _make_doc(cells=cells)
        expected = doc.nonempty_cell_count / doc.cell_count
        assert abs(doc.fill_ratio - expected) < 1e-9

    def test_alias_has_new_properties(self):
        doc = _make_doc()
        assert isinstance(doc, SylkDoc)
        assert hasattr(doc, "has_numeric_cells")
        assert hasattr(doc, "has_string_cells")
        assert hasattr(doc, "fill_ratio")

    def test_from_file_numeric_row(self):
        doc = SylkModelDocument.from_file(SAMPLES / "numeric-row.slk")
        assert isinstance(doc.has_numeric_cells, bool)
        assert isinstance(doc.has_string_cells, bool)
        assert 0.0 <= doc.fill_ratio <= 1.0
