"""R561: ODT dimension properties — is_empty, has_content, is_single_paragraph, has_headings.

Tests for OdtModelDocument dimension properties added in R561.
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


class TestIsEmpty:
    def test_no_paragraphs_is_empty(self):
        doc = _make_doc(paragraph_count=0)
        assert doc.is_empty is True

    def test_one_paragraph_not_empty(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.is_empty is False

    def test_multiple_paragraphs_not_empty(self):
        doc = _make_doc(paragraph_count=3)
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(paragraph_count=0)
        assert isinstance(doc.is_empty, bool)


class TestHasContent:
    def test_one_paragraph_has_content(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.has_content is True

    def test_multiple_paragraphs_has_content(self):
        doc = _make_doc(paragraph_count=5)
        assert doc.has_content is True

    def test_empty_no_content(self):
        doc = _make_doc(paragraph_count=0)
        assert doc.has_content is False

    def test_has_content_type(self):
        doc = _make_doc(paragraph_count=1)
        assert isinstance(doc.has_content, bool)


class TestIsSingleParagraph:
    def test_one_paragraph_is_single(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.is_single_paragraph is True

    def test_zero_not_single(self):
        doc = _make_doc(paragraph_count=0)
        assert doc.is_single_paragraph is False

    def test_two_not_single(self):
        doc = _make_doc(paragraph_count=2)
        assert doc.is_single_paragraph is False

    def test_is_single_paragraph_type(self):
        doc = _make_doc(paragraph_count=1)
        assert isinstance(doc.is_single_paragraph, bool)


class TestHasHeadings:
    def test_one_heading_has_headings(self):
        doc = _make_doc(heading_count=1)
        assert doc.has_headings is True

    def test_no_headings(self):
        doc = _make_doc(heading_count=0)
        assert doc.has_headings is False

    def test_multiple_headings(self):
        doc = _make_doc(heading_count=3)
        assert doc.has_headings is True

    def test_has_headings_type(self):
        doc = _make_doc(heading_count=0)
        assert isinstance(doc.has_headings, bool)


class TestDimensionConsistency:
    def test_empty_and_has_content_exclusive(self):
        for n in [0, 1, 2, 5]:
            doc = _make_doc(paragraph_count=n)
            assert doc.is_empty != doc.has_content

    def test_single_paragraph_implies_has_content(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.is_single_paragraph
        assert doc.has_content
        assert not doc.is_empty

    def test_alias_odt_doc_has_properties(self):
        doc = _make_doc(paragraph_count=2, heading_count=1)
        assert isinstance(doc, OdtDoc)
        assert hasattr(doc, "is_empty")
        assert hasattr(doc, "has_content")
        assert hasattr(doc, "has_headings")

    def test_from_file_two_paragraphs(self):
        doc = OdtModelDocument.from_file(SAMPLES / "two-paragraphs.odt")
        assert doc.has_content is True
        assert isinstance(doc.is_single_paragraph, bool)
        assert isinstance(doc.has_headings, bool)
