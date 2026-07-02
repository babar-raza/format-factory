"""Tests for R1253: CsvDocument density and shape analysis properties.

Properties under test:
    fill_density   — total non-empty cells / total_cell_count (0.0 if no cells)
    has_empty_cells — any cell in rows is an empty string
    aspect_ratio   — column_count / row_count (0.0 if no rows)

spec_fact_ref: FACT-CSV-001
"""

import sys
from pathlib import Path

import pytest

# FF csv accessed via direct path to avoid stdlib csv collision
_csv_ff_models = Path(__file__).resolve().parent.parent.parent.parent / "src" / "python" / "csv" / "models.py"
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("csv_ff_models", _csv_ff_models)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CsvDocument = _mod.CsvDocument


def _make_doc(rows: list[list[str]], headers: list[str] | None = None, delimiter: str = ",") -> CsvDocument:
    has_header = headers is not None and len(headers) > 0
    return CsvDocument({
        "rows": rows,
        "headers": headers or (rows[0] if rows else []),
        "row_count": len(rows),
        "has_header": has_header,
        "delimiter": delimiter,
    })


# ── fill_density ──────────────────────────────────────────────────────────────

class TestFillDensity:
    def test_all_filled_density_one(self):
        doc = _make_doc([["a", "b"], ["c", "d"]])
        assert doc.fill_density == pytest.approx(1.0)

    def test_no_cells_density_zero(self):
        doc = _make_doc([])
        assert doc.fill_density == pytest.approx(0.0)

    def test_half_empty_density_half(self):
        doc = _make_doc([["a", ""], ["", "d"]])
        assert doc.fill_density == pytest.approx(0.5)

    def test_all_empty_density_zero(self):
        doc = _make_doc([["", ""], ["", ""]])
        assert doc.fill_density == pytest.approx(0.0)

    def test_one_filled_cell(self):
        doc = _make_doc([["x", "", ""], ["", "", ""]])
        assert doc.fill_density == pytest.approx(1.0 / 6.0)


# ── has_empty_cells ───────────────────────────────────────────────────────────

class TestHasEmptyCells:
    def test_no_empty_cells(self):
        doc = _make_doc([["a", "b"], ["c", "d"]])
        assert doc.has_empty_cells is False

    def test_one_empty_cell(self):
        doc = _make_doc([["a", ""], ["c", "d"]])
        assert doc.has_empty_cells is True

    def test_all_empty_cells(self):
        doc = _make_doc([["", ""], ["", ""]])
        assert doc.has_empty_cells is True

    def test_empty_doc_no_empty_cells(self):
        doc = _make_doc([])
        assert doc.has_empty_cells is False

    def test_single_non_empty_cell(self):
        doc = _make_doc([["hello"]])
        assert doc.has_empty_cells is False


# ── aspect_ratio ──────────────────────────────────────────────────────────────

class TestAspectRatio:
    def test_no_rows_returns_zero(self):
        doc = _make_doc([])
        assert doc.aspect_ratio == pytest.approx(0.0)

    def test_square_doc_ratio_one(self):
        doc = _make_doc([["a", "b"], ["c", "d"]])
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_wide_doc_ratio_gt_one(self):
        doc = _make_doc([["a", "b", "c"]])
        assert doc.aspect_ratio == pytest.approx(3.0)

    def test_tall_doc_ratio_lt_one(self):
        doc = _make_doc([["a"]] * 3)
        assert doc.aspect_ratio == pytest.approx(1.0 / 3.0)

    def test_two_cols_four_rows(self):
        doc = _make_doc([["a", "b"]] * 4)
        assert doc.aspect_ratio == pytest.approx(0.5)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_full_doc_no_empty_cells_density_one(self):
        doc = _make_doc([["x", "y"], ["a", "b"]])
        assert doc.has_empty_cells is False
        assert doc.fill_density == pytest.approx(1.0)

    def test_aspect_ratio_matches_shape(self):
        doc = _make_doc([["a", "b", "c"], ["d", "e", "f"]])
        assert doc.aspect_ratio == pytest.approx(doc.column_count / doc.row_count)
