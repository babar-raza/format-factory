"""R560: ABW dimension properties — is_empty, has_content, is_single_paragraph.

Tests for AbwDocument dimension properties added in R560.
Spec refs: FACT-ABW-001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.models import AbwDocument

SAMPLES = Path("samples/by-format/abw")


def _make_doc(paragraph_count=0, paragraphs=None, section_count=1):
    """Build a minimal AbwDocument from a dict."""
    if paragraphs is None:
        paragraphs = [f"Para {i}" for i in range(paragraph_count)]
    return AbwDocument({
        "is_abw": True,
        "section_count": section_count,
        "paragraph_count": paragraph_count,
        "paragraphs": paragraphs,
    })


class TestIsEmpty:
    def test_zero_paragraphs_is_empty(self):
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
        doc = _make_doc(paragraph_count=3)
        assert doc.has_content is True

    def test_zero_paragraphs_no_content(self):
        doc = _make_doc(paragraph_count=0)
        assert doc.has_content is False

    def test_has_content_type(self):
        doc = _make_doc(paragraph_count=1)
        assert isinstance(doc.has_content, bool)


class TestIsSingleParagraph:
    def test_one_paragraph_is_single(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.is_single_paragraph is True

    def test_zero_paragraphs_not_single(self):
        doc = _make_doc(paragraph_count=0)
        assert doc.is_single_paragraph is False

    def test_two_paragraphs_not_single(self):
        doc = _make_doc(paragraph_count=2)
        assert doc.is_single_paragraph is False

    def test_is_single_paragraph_type(self):
        doc = _make_doc(paragraph_count=1)
        assert isinstance(doc.is_single_paragraph, bool)


class TestDimensionConsistency:
    def test_empty_and_has_content_mutually_exclusive(self):
        for n in [0, 1, 2, 5]:
            doc = _make_doc(paragraph_count=n)
            assert doc.is_empty != doc.has_content

    def test_single_implies_has_content(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.is_single_paragraph
        assert doc.has_content
        assert not doc.is_empty

    def test_from_file_minimal_document(self):
        doc = AbwDocument.from_file(SAMPLES / "minimal-document.abw")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.has_content, bool)
        assert isinstance(doc.is_single_paragraph, bool)

    def test_from_file_two_paragraphs(self):
        doc = AbwDocument.from_file(SAMPLES / "two-paragraphs.abw")
        assert doc.has_content is True
        assert isinstance(doc.is_single_paragraph, bool)
