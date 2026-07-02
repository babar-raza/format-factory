"""Tests for R1250: SylkModelDocument grid geometry and composition properties.

Properties under test:
    is_square     — row_count == col_count and row_count > 0
    has_mixed_types — has_numeric_cells and has_string_cells
    numeric_ratio — numeric_cell_count / nonempty_cell_count (0.0 if no non-empty)

spec_fact_ref: FACT-SYLK-001
"""

import types
import pytest
from sylk.models import SylkModelDocument


def _make_cell(value_type: str = "numeric", value=0):
    return types.SimpleNamespace(value_type=value_type, value=value, text=str(value))


def _make_doc(rows: int, cols: int, cells: list | None = None) -> SylkModelDocument:
    """Build a SylkModelDocument stub.

    cells: list of SimpleNamespace with value_type in ['numeric','string','empty','']
    If not provided, builds rows*cols numeric cells.
    """
    if cells is None:
        cells = [_make_cell("numeric", i) for i in range(rows * cols)]
    parsed = types.SimpleNamespace(
        rows=rows,
        cols=cols,
        cell_count=rows * cols,
        cells=cells,
        path="test.slk",
        id_line="ID;P",
    )
    return SylkModelDocument(parsed)


def _make_doc_with_cells(rows: int, cols: int, cell_types: list[str]) -> SylkModelDocument:
    """Build with specific cell types."""
    cells = [_make_cell(ct, i if ct == "numeric" else "text") for i, ct in enumerate(cell_types)]
    parsed = types.SimpleNamespace(
        rows=rows,
        cols=cols,
        cell_count=rows * cols,
        cells=cells,
        path="test.slk",
        id_line="ID;P",
    )
    return SylkModelDocument(parsed)


# ── is_square ─────────────────────────────────────────────────────────────────

class TestIsSquare:
    def test_equal_rows_and_cols_is_square(self):
        doc = _make_doc(5, 5)
        assert doc.is_square is True

    def test_unequal_not_square(self):
        doc = _make_doc(5, 10)
        assert doc.is_square is False

    def test_zero_rows_not_square(self):
        doc = _make_doc(0, 0)
        assert doc.is_square is False

    def test_single_cell_is_square(self):
        doc = _make_doc(1, 1)
        assert doc.is_square is True

    def test_more_cols_not_square(self):
        doc = _make_doc(3, 7)
        assert doc.is_square is False


# ── has_mixed_types ───────────────────────────────────────────────────────────

class TestHasMixedTypes:
    def test_numeric_and_string_is_mixed(self):
        doc = _make_doc_with_cells(2, 2, ["numeric", "numeric", "string", "string"])
        assert doc.has_mixed_types is True

    def test_all_numeric_not_mixed(self):
        doc = _make_doc_with_cells(2, 2, ["numeric", "numeric", "numeric", "numeric"])
        assert doc.has_mixed_types is False

    def test_all_string_not_mixed(self):
        doc = _make_doc_with_cells(2, 2, ["string", "string", "string", "string"])
        assert doc.has_mixed_types is False

    def test_empty_doc_not_mixed(self):
        doc = _make_doc(0, 0, cells=[])
        assert doc.has_mixed_types is False

    def test_single_numeric_not_mixed(self):
        doc = _make_doc_with_cells(1, 1, ["numeric"])
        assert doc.has_mixed_types is False

    def test_one_numeric_one_string_is_mixed(self):
        doc = _make_doc_with_cells(1, 2, ["numeric", "string"])
        assert doc.has_mixed_types is True


# ── numeric_ratio ─────────────────────────────────────────────────────────────

class TestNumericRatio:
    def test_all_numeric_ratio_one(self):
        doc = _make_doc_with_cells(2, 2, ["numeric", "numeric", "numeric", "numeric"])
        assert doc.numeric_ratio == pytest.approx(1.0)

    def test_all_string_ratio_zero(self):
        doc = _make_doc_with_cells(2, 2, ["string", "string", "string", "string"])
        assert doc.numeric_ratio == pytest.approx(0.0)

    def test_half_numeric_ratio_half(self):
        doc = _make_doc_with_cells(2, 2, ["numeric", "numeric", "string", "string"])
        assert doc.numeric_ratio == pytest.approx(0.5)

    def test_empty_doc_ratio_zero(self):
        doc = _make_doc(0, 0, cells=[])
        assert doc.numeric_ratio == 0.0

    def test_mixed_three_quarters_numeric(self):
        doc = _make_doc_with_cells(2, 2, ["numeric", "numeric", "numeric", "string"])
        assert doc.numeric_ratio == pytest.approx(0.75)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_mixed_has_nonzero_numeric_ratio(self):
        doc = _make_doc_with_cells(2, 2, ["numeric", "string", "numeric", "string"])
        assert doc.has_mixed_types is True
        assert 0.0 < doc.numeric_ratio < 1.0

    def test_square_all_numeric(self):
        doc = _make_doc(3, 3)
        assert doc.is_square is True
        assert doc.numeric_ratio == pytest.approx(1.0)

    def test_numeric_ratio_consistency(self):
        doc = _make_doc_with_cells(1, 3, ["numeric", "string", "numeric"])
        assert doc.numeric_ratio == pytest.approx(2 / 3)
        assert doc.has_mixed_types is True
