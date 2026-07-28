"""Tests for R1270: SylkModelDocument cell type distribution analysis properties.

Properties under test:
    string_ratio       — string_cell_count / nonempty_cell_count (0.0 if empty)
    is_numeric_dominant — numeric_ratio > 0.5
    is_all_numeric     — all non-empty cells are numeric

spec_fact_ref: SAL-SYLK-00001
"""

import types
import pytest
from sylk.models import SylkModelDocument


def _make_cell(value, type_: str) -> types.SimpleNamespace:
    return types.SimpleNamespace(value=value, value_type=type_)


def _make_doc(numeric: int, string: int, empty: int = 0) -> SylkModelDocument:
    """Build a SylkModelDocument stub with given cell counts."""
    cells = (
        [_make_cell(float(i), "numeric") for i in range(numeric)]
        + [_make_cell(f"s{i}", "string") for i in range(string)]
        + [_make_cell(None, "empty") for _ in range(empty)]
    )
    parsed = types.SimpleNamespace(
        rows=numeric + string + empty,
        cols=1,
        cells=cells,
        path="test.slk",
        id_line="ID;P",
    )
    return SylkModelDocument(parsed)


# ── string_ratio ──────────────────────────────────────────────────────────────

class TestStringRatio:
    def test_no_cells_returns_zero(self):
        doc = _make_doc(0, 0)
        assert doc.string_ratio == pytest.approx(0.0)

    def test_all_strings(self):
        doc = _make_doc(0, 10)
        assert doc.string_ratio == pytest.approx(1.0)

    def test_no_strings(self):
        doc = _make_doc(10, 0)
        assert doc.string_ratio == pytest.approx(0.0)

    def test_half_strings(self):
        doc = _make_doc(5, 5)
        assert doc.string_ratio == pytest.approx(0.5)

    def test_one_string_of_four(self):
        doc = _make_doc(3, 1)
        assert doc.string_ratio == pytest.approx(0.25)

    def test_ratio_plus_numeric_ratio_equals_one(self):
        doc = _make_doc(7, 3)
        assert doc.string_ratio + doc.numeric_ratio == pytest.approx(1.0)


# ── is_numeric_dominant ───────────────────────────────────────────────────────

class TestIsNumericDominant:
    def test_all_numeric_is_dominant(self):
        doc = _make_doc(10, 0)
        assert doc.is_numeric_dominant is True

    def test_exactly_50_pct_not_dominant(self):
        doc = _make_doc(5, 5)
        assert doc.is_numeric_dominant is False

    def test_majority_numeric_is_dominant(self):
        doc = _make_doc(6, 4)
        assert doc.is_numeric_dominant is True

    def test_all_strings_not_dominant(self):
        doc = _make_doc(0, 10)
        assert doc.is_numeric_dominant is False

    def test_empty_not_dominant(self):
        doc = _make_doc(0, 0)
        assert doc.is_numeric_dominant is False


# ── is_all_numeric ────────────────────────────────────────────────────────────

class TestIsAllNumeric:
    def test_all_numeric_cells(self):
        doc = _make_doc(5, 0)
        assert doc.is_all_numeric is True

    def test_mixed_not_all_numeric(self):
        doc = _make_doc(5, 1)
        assert doc.is_all_numeric is False

    def test_all_strings_not_all_numeric(self):
        doc = _make_doc(0, 5)
        assert doc.is_all_numeric is False

    def test_empty_doc_not_all_numeric(self):
        doc = _make_doc(0, 0)
        assert doc.is_all_numeric is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_all_numeric_implies_dominant(self):
        doc = _make_doc(5, 0)
        assert doc.is_all_numeric is True
        assert doc.is_numeric_dominant is True

    def test_all_numeric_string_ratio_zero(self):
        doc = _make_doc(5, 0)
        assert doc.is_all_numeric is True
        assert doc.string_ratio == pytest.approx(0.0)

    def test_mixed_types_consistent_with_ratios(self):
        doc = _make_doc(7, 3)
        assert doc.has_mixed_types is True
        assert doc.numeric_ratio == pytest.approx(0.7)
        assert doc.string_ratio == pytest.approx(0.3)

    def test_dominant_and_not_all_numeric(self):
        # 6 numeric, 4 string → numeric > 50% but not all
        doc = _make_doc(6, 4)
        assert doc.is_numeric_dominant is True
        assert doc.is_all_numeric is False
