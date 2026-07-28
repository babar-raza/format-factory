"""Tests for R1286: SylkModelDocument cell type homogeneity properties.

Properties under test:
    is_all_string      — all non-empty cells are strings (no numeric cells)
    has_single_type    — all non-empty cells share one type (all numeric or all string)
    is_string_dominant — string_ratio > 0.5

spec_fact_ref: SAL-SYLK-00001
"""

import types
import pytest
from sylk.models import SylkModelDocument


def _make_cell(value_type: str, value=None) -> types.SimpleNamespace:
    return types.SimpleNamespace(value_type=value_type, value=value)


def _make_doc(cell_types: list[str]) -> SylkModelDocument:
    cells = [_make_cell(t) for t in cell_types]
    parsed = types.SimpleNamespace(
        rows=1,
        cols=len(cell_types) or 1,
        cells=cells,
        path="test.slk",
    )
    return SylkModelDocument(parsed)


# ── is_all_string ─────────────────────────────────────────────────────────────

class TestIsAllString:
    def test_empty_doc_false(self):
        doc = _make_doc([])
        assert doc.is_all_string is False

    def test_all_empty_cells_false(self):
        doc = _make_doc(["empty", "empty"])
        assert doc.is_all_string is False

    def test_all_strings_true(self):
        doc = _make_doc(["string", "string", "string"])
        assert doc.is_all_string is True

    def test_mixed_string_and_numeric_false(self):
        doc = _make_doc(["string", "numeric"])
        assert doc.is_all_string is False

    def test_one_numeric_among_strings_false(self):
        doc = _make_doc(["string", "string", "numeric"])
        assert doc.is_all_string is False

    def test_strings_with_empty_cells_true(self):
        # empty cells don't count
        doc = _make_doc(["string", "empty", "string"])
        assert doc.is_all_string is True


# ── has_single_type ───────────────────────────────────────────────────────────

class TestHasSingleType:
    def test_empty_doc_false(self):
        doc = _make_doc([])
        assert doc.has_single_type is False

    def test_all_empty_false(self):
        doc = _make_doc(["empty", "empty"])
        assert doc.has_single_type is False

    def test_all_numeric_true(self):
        doc = _make_doc(["numeric", "numeric"])
        assert doc.has_single_type is True

    def test_all_string_true(self):
        doc = _make_doc(["string", "string"])
        assert doc.has_single_type is True

    def test_mixed_false(self):
        doc = _make_doc(["string", "numeric"])
        assert doc.has_single_type is False

    def test_numeric_with_empty_true(self):
        doc = _make_doc(["numeric", "empty", "numeric"])
        assert doc.has_single_type is True


# ── is_string_dominant ────────────────────────────────────────────────────────

class TestIsStringDominant:
    def test_no_nonempty_cells_false(self):
        doc = _make_doc(["empty", "empty"])
        assert doc.is_string_dominant is False

    def test_all_strings_dominant(self):
        doc = _make_doc(["string", "string"])
        assert doc.is_string_dominant is True

    def test_all_numeric_not_dominant(self):
        doc = _make_doc(["numeric", "numeric"])
        assert doc.is_string_dominant is False

    def test_more_strings_dominant(self):
        # 3 strings, 1 numeric → ratio = 0.75 > 0.5
        doc = _make_doc(["string", "string", "string", "numeric"])
        assert doc.is_string_dominant is True

    def test_equal_split_not_dominant(self):
        # ratio = 0.5, NOT > 0.5
        doc = _make_doc(["string", "numeric"])
        assert doc.is_string_dominant is False

    def test_more_numeric_not_dominant(self):
        doc = _make_doc(["numeric", "numeric", "string"])
        assert doc.is_string_dominant is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_all_string_implies_single_type(self):
        doc = _make_doc(["string", "string"])
        assert doc.is_all_string is True
        assert doc.has_single_type is True

    def test_all_numeric_implies_single_type_not_string(self):
        doc = _make_doc(["numeric", "numeric"])
        assert doc.is_all_numeric is True
        assert doc.has_single_type is True
        assert doc.is_all_string is False

    def test_mixed_neither_all_string_nor_all_numeric(self):
        doc = _make_doc(["string", "numeric"])
        assert doc.is_all_string is False
        assert doc.is_all_numeric is False
        assert doc.has_single_type is False
