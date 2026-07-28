"""R564: ABW section and paragraph analysis properties — has_sections, has_multiple_paragraphs, is_multi_section.

Tests for AbwDocument structural properties added in R564.
Spec refs: SAL-ABW-00001 (abiword:document, abiword:section, abiword:p).
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.models import AbwDocument

SAMPLES = Path("samples/by-format/abw")


def _make_doc(section_count=0, paragraph_count=0):
    """Build a minimal AbwDocument from counts."""
    data = {
        "is_abw": True,
        "section_count": section_count,
        "paragraph_count": paragraph_count,
        "paragraphs": [f"para {i}" for i in range(paragraph_count)],
    }
    return AbwDocument(data)


class TestHasSections:
    def test_no_sections(self):
        doc = _make_doc(section_count=0)
        assert doc.has_sections is False

    def test_one_section(self):
        doc = _make_doc(section_count=1)
        assert doc.has_sections is True

    def test_multiple_sections(self):
        doc = _make_doc(section_count=3)
        assert doc.has_sections is True

    def test_has_sections_type(self):
        doc = _make_doc(section_count=1)
        assert isinstance(doc.has_sections, bool)

    def test_has_sections_inverse_of_no_sections(self):
        doc0 = _make_doc(section_count=0)
        doc1 = _make_doc(section_count=1)
        assert doc0.has_sections is False
        assert doc1.has_sections is True


class TestHasMultipleParagraphs:
    def test_no_paragraphs(self):
        doc = _make_doc(paragraph_count=0)
        assert doc.has_multiple_paragraphs is False

    def test_one_paragraph(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.has_multiple_paragraphs is False

    def test_two_paragraphs(self):
        doc = _make_doc(paragraph_count=2)
        assert doc.has_multiple_paragraphs is True

    def test_many_paragraphs(self):
        doc = _make_doc(paragraph_count=10)
        assert doc.has_multiple_paragraphs is True

    def test_has_multiple_paragraphs_type(self):
        doc = _make_doc(paragraph_count=2)
        assert isinstance(doc.has_multiple_paragraphs, bool)


class TestIsMultiSection:
    def test_zero_sections_not_multi(self):
        doc = _make_doc(section_count=0)
        assert doc.is_multi_section is False

    def test_one_section_not_multi(self):
        doc = _make_doc(section_count=1)
        assert doc.is_multi_section is False

    def test_two_sections_is_multi(self):
        doc = _make_doc(section_count=2)
        assert doc.is_multi_section is True

    def test_many_sections_is_multi(self):
        doc = _make_doc(section_count=5)
        assert doc.is_multi_section is True

    def test_is_multi_section_type(self):
        doc = _make_doc(section_count=2)
        assert isinstance(doc.is_multi_section, bool)


class TestSectionParagraphConsistency:
    def test_has_sections_implies_section_count_positive(self):
        doc = _make_doc(section_count=2)
        assert doc.has_sections
        assert doc.section_count > 0

    def test_is_multi_section_implies_has_sections(self):
        doc = _make_doc(section_count=3)
        assert doc.is_multi_section
        assert doc.has_sections

    def test_single_paragraph_not_multiple(self):
        doc = _make_doc(paragraph_count=1)
        assert doc.is_single_paragraph is True
        assert doc.has_multiple_paragraphs is False

    def test_from_file(self):
        doc = AbwDocument.from_file(SAMPLES / "two-paragraphs.abw")
        assert isinstance(doc.has_sections, bool)
        assert isinstance(doc.has_multiple_paragraphs, bool)
        assert isinstance(doc.is_multi_section, bool)
        assert doc.has_multiple_paragraphs is True
