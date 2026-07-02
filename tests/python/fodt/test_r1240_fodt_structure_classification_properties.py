"""Tests for R1240: FodtDocument structure classification properties.

Properties under test:
    paragraph_count — number of "paragraph" kind blocks (non-heading)
    has_lists       — list_count > 0
    is_complex      — has_tables or has_lists or has_headings

spec_fact_ref: FACT-FODT-001
"""

import pytest
from fodt.models import FodtDocument


def _make_doc(
    blocks: list[dict] | None = None,
    tables: list[dict] | None = None,
    lists: list[dict] | None = None,
) -> FodtDocument:
    """Build a FodtDocument stub with given blocks, tables, and lists."""
    return FodtDocument({
        "format_id": "fodt",
        "odf_version": "1.3",
        "blocks": blocks or [],
        "tables": tables or [],
        "lists": lists or [],
        "warnings": [],
    })


def _para(text: str = "Hello") -> dict:
    return {"kind": "paragraph", "text": text, "style_name": "Text_20_Body", "spans": []}


def _heading(text: str = "Title", level: int = 1) -> dict:
    return {"kind": "heading", "text": text, "style_name": "Heading_20_1", "outline_level": level, "spans": []}


def _table() -> dict:
    return {"rows": [], "style_name": "Table1"}


def _list_item() -> dict:
    return {"items": [{"text": "Item 1"}], "style_name": "List_20_Bullet"}


# ── paragraph_count ───────────────────────────────────────────────────────────

class TestParagraphCount:
    def test_no_blocks_returns_zero(self):
        doc = _make_doc()
        assert doc.paragraph_count == 0

    def test_single_paragraph(self):
        doc = _make_doc(blocks=[_para()])
        assert doc.paragraph_count == 1

    def test_three_paragraphs(self):
        doc = _make_doc(blocks=[_para(), _para("A"), _para("B")])
        assert doc.paragraph_count == 3

    def test_headings_excluded_from_count(self):
        doc = _make_doc(blocks=[_heading(), _para()])
        assert doc.paragraph_count == 1

    def test_only_headings_returns_zero(self):
        doc = _make_doc(blocks=[_heading(), _heading("Sec 2")])
        assert doc.paragraph_count == 0

    def test_mixed_blocks_counts_paragraphs_only(self):
        doc = _make_doc(blocks=[_heading(), _para(), _heading("B"), _para("C"), _para("D")])
        assert doc.paragraph_count == 3


# ── has_lists ─────────────────────────────────────────────────────────────────

class TestHasLists:
    def test_no_lists_returns_false(self):
        doc = _make_doc()
        assert doc.has_lists is False

    def test_one_list_returns_true(self):
        doc = _make_doc(lists=[_list_item()])
        assert doc.has_lists is True

    def test_multiple_lists_returns_true(self):
        doc = _make_doc(lists=[_list_item(), _list_item()])
        assert doc.has_lists is True

    def test_has_lists_consistent_with_list_count(self):
        doc = _make_doc(lists=[_list_item()])
        assert doc.has_lists is True
        assert doc.list_count == 1

    def test_no_lists_list_count_zero(self):
        doc = _make_doc()
        assert doc.has_lists is False
        assert doc.list_count == 0


# ── is_complex ────────────────────────────────────────────────────────────────

class TestIsComplex:
    def test_empty_document_not_complex(self):
        doc = _make_doc()
        assert doc.is_complex is False

    def test_only_paragraphs_not_complex(self):
        doc = _make_doc(blocks=[_para(), _para()])
        assert doc.is_complex is False

    def test_has_table_is_complex(self):
        doc = _make_doc(blocks=[_para()], tables=[_table()])
        assert doc.is_complex is True

    def test_has_list_is_complex(self):
        doc = _make_doc(blocks=[_para()], lists=[_list_item()])
        assert doc.is_complex is True

    def test_has_heading_is_complex(self):
        doc = _make_doc(blocks=[_heading(), _para()])
        assert doc.is_complex is True

    def test_all_complex_elements(self):
        doc = _make_doc(
            blocks=[_heading(), _para()],
            tables=[_table()],
            lists=[_list_item()],
        )
        assert doc.is_complex is True

    def test_not_complex_no_tables_lists_headings(self):
        doc = _make_doc(blocks=[_para("A"), _para("B"), _para("C")])
        assert doc.is_complex is False
        assert doc.paragraph_count == 3


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_paragraph_count_less_than_block_count_with_headings(self):
        doc = _make_doc(blocks=[_heading(), _para(), _para()])
        assert doc.paragraph_count == 2
        assert doc.block_count == 3

    def test_is_complex_when_has_headings_and_no_tables_lists(self):
        doc = _make_doc(blocks=[_heading()])
        assert doc.has_headings is True
        assert doc.has_tables is False
        assert doc.has_lists is False
        assert doc.is_complex is True

    def test_consistent_with_block_count(self):
        doc = _make_doc(blocks=[_para(), _para()])
        assert doc.paragraph_count + doc.heading_count == doc.block_count
