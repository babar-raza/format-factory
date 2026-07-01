"""R568: FODT structural properties — heading_count, is_multi_block, has_tables.

Tests for FodtDocument structural properties added in R568.
Spec refs: FACT-FODT-001, FACT-FODT-003.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.models import FodtDocument

SAMPLES = Path("samples/by-format/fodt")


def _make_doc(paragraphs=0, headings=0, tables=0):
    """Build a minimal FodtDocument from a dict."""
    blocks = (
        [{"kind": "paragraph", "text": f"Para {i}", "style_name": "Text_Body", "spans": []} for i in range(paragraphs)]
        + [{"kind": "heading", "text": f"Head {i}", "style_name": "Heading_1", "outline_level": 1, "spans": []} for i in range(headings)]
    )
    table_list = [{"rows": []} for _ in range(tables)]
    return FodtDocument({
        "format_id": "fodt",
        "blocks": blocks,
        "tables": table_list,
        "lists": [],
    })


class TestHeadingCount:
    def test_one_heading(self):
        doc = _make_doc(headings=1)
        assert doc.heading_count == 1

    def test_multiple_headings(self):
        doc = _make_doc(headings=3)
        assert doc.heading_count == 3

    def test_no_headings(self):
        doc = _make_doc(paragraphs=2, headings=0)
        assert doc.heading_count == 0

    def test_heading_count_type(self):
        doc = _make_doc(headings=1)
        assert isinstance(doc.heading_count, int)

    def test_heading_count_consistent_with_has_headings(self):
        for n in range(5):
            doc = _make_doc(headings=n)
            assert doc.has_headings == (n > 0)
            assert doc.heading_count == n


class TestIsMultiBlock:
    def test_two_blocks_is_multi(self):
        doc = _make_doc(paragraphs=2)
        assert doc.is_multi_block is True

    def test_one_block_not_multi(self):
        doc = _make_doc(paragraphs=1)
        assert doc.is_multi_block is False

    def test_zero_blocks_not_multi(self):
        doc = _make_doc()
        assert doc.is_multi_block is False

    def test_heading_and_para_is_multi(self):
        doc = _make_doc(paragraphs=1, headings=1)
        assert doc.is_multi_block is True

    def test_is_multi_block_type(self):
        doc = _make_doc(paragraphs=2)
        assert isinstance(doc.is_multi_block, bool)

    def test_is_multi_block_consistent_with_block_count(self):
        for n in range(5):
            doc = _make_doc(paragraphs=n)
            assert doc.is_multi_block == (n > 1)


class TestHasTables:
    def test_one_table_has_tables(self):
        doc = _make_doc(tables=1)
        assert doc.has_tables is True

    def test_multiple_tables_has_tables(self):
        doc = _make_doc(tables=3)
        assert doc.has_tables is True

    def test_no_tables(self):
        doc = _make_doc(paragraphs=2, tables=0)
        assert doc.has_tables is False

    def test_has_tables_type(self):
        doc = _make_doc()
        assert isinstance(doc.has_tables, bool)

    def test_has_tables_consistent_with_table_count(self):
        for n in range(4):
            doc = _make_doc(tables=n)
            assert doc.has_tables == (n > 0)
            assert doc.table_count == n


class TestStructuralConsistency:
    def test_multi_block_implies_has_content(self):
        doc = _make_doc(paragraphs=2)
        assert doc.is_multi_block
        assert doc.has_content
        assert not doc.is_single_block

    def test_heading_count_le_block_count(self):
        for p in range(4):
            for h in range(4):
                doc = _make_doc(paragraphs=p, headings=h)
                assert doc.heading_count <= doc.block_count

    def test_from_file_table_basic(self):
        doc = FodtDocument.from_file(SAMPLES / "table-basic.fodt")
        assert doc.has_tables is True
        assert isinstance(doc.heading_count, int)
        assert isinstance(doc.is_multi_block, bool)

    def test_from_file_headings_and_paragraphs(self):
        doc = FodtDocument.from_file(SAMPLES / "headings-and-paragraphs.fodt")
        assert isinstance(doc.heading_count, int)
        assert isinstance(doc.is_multi_block, bool)
        assert isinstance(doc.has_tables, bool)
