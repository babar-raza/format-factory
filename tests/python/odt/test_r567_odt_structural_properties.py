"""R567: ODT structural properties — is_multi_paragraph, has_multiple_headings, total_block_count.

Tests for OdtModelDocument structural properties added in R567.
Spec refs: SAL-ODT-01067.
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.models import OdtModelDocument, OdtDoc

SAMPLES = Path("samples/by-format/odt/valid")


def _make_doc(paragraph_count=0, heading_count=0):
    """Build a minimal OdtModelDocument from a stub parsed object."""
    paragraphs = [types.SimpleNamespace(text=f"Para {i}") for i in range(paragraph_count)]
    headings = [types.SimpleNamespace(text=f"Head {i}") for i in range(heading_count)]
    return OdtModelDocument(types.SimpleNamespace(
        paragraphs=paragraphs,
        headings=headings,
        path="test.odt",
    ))


class TestIsMultiParagraph:
    def test_two_paragraphs_is_multi(self):
        doc = _make_doc(paragraph_count=2)
        assert doc.is_multi_paragraph is True

    def test_one_paragraph_not_multi(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.is_multi_paragraph is False

    def test_zero_paragraphs_not_multi(self):
        doc = _make_doc(paragraph_count=0)
        assert doc.is_multi_paragraph is False

    def test_five_paragraphs_is_multi(self):
        doc = _make_doc(paragraph_count=5)
        assert doc.is_multi_paragraph is True

    def test_is_multi_paragraph_type(self):
        doc = _make_doc(paragraph_count=2)
        assert isinstance(doc.is_multi_paragraph, bool)


class TestHasMultipleHeadings:
    def test_two_headings_multiple(self):
        doc = _make_doc(heading_count=2)
        assert doc.has_multiple_headings is True

    def test_one_heading_not_multiple(self):
        doc = _make_doc(heading_count=1)
        assert doc.has_multiple_headings is False

    def test_zero_headings_not_multiple(self):
        doc = _make_doc(heading_count=0)
        assert doc.has_multiple_headings is False

    def test_three_headings_multiple(self):
        doc = _make_doc(heading_count=3)
        assert doc.has_multiple_headings is True

    def test_has_multiple_headings_type(self):
        doc = _make_doc(heading_count=0)
        assert isinstance(doc.has_multiple_headings, bool)


class TestTotalBlockCount:
    def test_zero_paragraphs_zero_headings(self):
        doc = _make_doc(paragraph_count=0, heading_count=0)
        assert doc.total_block_count == 0

    def test_paragraphs_only(self):
        doc = _make_doc(paragraph_count=3, heading_count=0)
        assert doc.total_block_count == 3

    def test_headings_only(self):
        doc = _make_doc(paragraph_count=0, heading_count=2)
        assert doc.total_block_count == 2

    def test_paragraphs_and_headings_sum(self):
        doc = _make_doc(paragraph_count=4, heading_count=3)
        assert doc.total_block_count == 7

    def test_total_block_count_type(self):
        doc = _make_doc(paragraph_count=1, heading_count=1)
        assert isinstance(doc.total_block_count, int)

    def test_total_block_count_ge_paragraph_count(self):
        for p in range(5):
            for h in range(5):
                doc = _make_doc(paragraph_count=p, heading_count=h)
                assert doc.total_block_count >= doc.paragraph_count
                assert doc.total_block_count >= doc.heading_count


class TestStructuralConsistency:
    def test_multi_paragraph_implies_has_content(self):
        doc = _make_doc(paragraph_count=3)
        assert doc.is_multi_paragraph
        assert doc.has_content
        assert not doc.is_single_paragraph

    def test_multiple_headings_implies_has_headings(self):
        doc = _make_doc(heading_count=2)
        assert doc.has_multiple_headings
        assert doc.has_headings

    def test_total_block_count_equals_sum(self):
        doc = _make_doc(paragraph_count=2, heading_count=1)
        assert doc.total_block_count == doc.paragraph_count + doc.heading_count

    def test_alias_has_new_properties(self):
        doc = _make_doc(paragraph_count=2, heading_count=2)
        assert isinstance(doc, OdtDoc)
        assert hasattr(doc, "is_multi_paragraph")
        assert hasattr(doc, "has_multiple_headings")
        assert hasattr(doc, "total_block_count")

    def test_from_file_two_paragraphs(self):
        doc = OdtModelDocument.from_file(SAMPLES / "two-paragraphs.odt")
        assert doc.is_multi_paragraph is True
        assert isinstance(doc.has_multiple_headings, bool)
        assert doc.total_block_count >= doc.paragraph_count
