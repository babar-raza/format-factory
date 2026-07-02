"""Tests for R1251: AbwDocument scale and density properties.

Properties under test:
    is_large             — paragraph_count > 50
    is_text_heavy        — total_text_length > 5000
    paragraphs_per_section — paragraph_count / section_count (0.0 if no sections)

spec_fact_ref: FACT-ABW-001
"""

import pytest
from abw.models import AbwDocument


def _make_doc(paragraphs: list[str], section_count: int = 1) -> AbwDocument:
    return AbwDocument({
        "is_abw": True,
        "section_count": section_count,
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    })


# ── is_large ─────────────────────────────────────────────────────────────────

class TestIsLarge:
    def test_51_paragraphs_is_large(self):
        doc = _make_doc(["p"] * 51)
        assert doc.is_large is True

    def test_50_paragraphs_not_large(self):
        doc = _make_doc(["p"] * 50)
        assert doc.is_large is False

    def test_empty_not_large(self):
        doc = _make_doc([])
        assert doc.is_large is False

    def test_one_paragraph_not_large(self):
        doc = _make_doc(["hello"])
        assert doc.is_large is False

    def test_100_paragraphs_is_large(self):
        doc = _make_doc(["x"] * 100)
        assert doc.is_large is True


# ── is_text_heavy ─────────────────────────────────────────────────────────────

class TestIsTextHeavy:
    def test_long_text_is_heavy(self):
        doc = _make_doc(["a" * 5001])
        assert doc.is_text_heavy is True

    def test_exactly_5000_not_heavy(self):
        doc = _make_doc(["a" * 5000])
        assert doc.is_text_heavy is False

    def test_empty_not_heavy(self):
        doc = _make_doc([])
        assert doc.is_text_heavy is False

    def test_many_short_paragraphs_accumulate(self):
        # 51 paragraphs of 100 chars = 5100 total → heavy
        doc = _make_doc(["a" * 100] * 51)
        assert doc.is_text_heavy is True

    def test_few_short_paragraphs_not_heavy(self):
        doc = _make_doc(["hello world"] * 5)
        assert doc.is_text_heavy is False


# ── paragraphs_per_section ────────────────────────────────────────────────────

class TestParagraphsPerSection:
    def test_no_sections_returns_zero(self):
        doc = _make_doc(["p1", "p2"], section_count=0)
        assert doc.paragraphs_per_section == 0.0

    def test_one_section_three_paragraphs(self):
        doc = _make_doc(["p1", "p2", "p3"], section_count=1)
        assert doc.paragraphs_per_section == pytest.approx(3.0)

    def test_two_sections_four_paragraphs(self):
        doc = _make_doc(["p"] * 4, section_count=2)
        assert doc.paragraphs_per_section == pytest.approx(2.0)

    def test_three_sections_nine_paragraphs(self):
        doc = _make_doc(["p"] * 9, section_count=3)
        assert doc.paragraphs_per_section == pytest.approx(3.0)

    def test_empty_paragraphs_with_sections(self):
        doc = _make_doc([], section_count=2)
        assert doc.paragraphs_per_section == pytest.approx(0.0)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_large_doc_may_be_text_heavy(self):
        doc = _make_doc(["a" * 100] * 60)
        assert doc.is_large is True
        assert doc.is_text_heavy is True

    def test_large_doc_short_text_not_heavy(self):
        doc = _make_doc(["x"] * 60)
        assert doc.is_large is True
        assert doc.is_text_heavy is False

    def test_paragraphs_per_section_consistent_with_counts(self):
        doc = _make_doc(["p"] * 10, section_count=5)
        assert doc.paragraphs_per_section == pytest.approx(doc.paragraph_count / doc.section_count)
