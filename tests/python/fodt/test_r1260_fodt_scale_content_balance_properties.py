"""Tests for R1260: FodtDocument scale and content balance properties.

Properties under test:
    total_block_count — paragraph_count + heading_count
    heading_ratio     — heading_count / total_block_count (0.0 if no blocks)
    is_outline_heavy  — heading_ratio > 0.3

spec_fact_ref: FACT-FODT-001
"""

import pytest
from fodt.models import FodtDocument


def _make_doc(paragraphs: int, headings: int, tables: int = 0, lists: int = 0) -> FodtDocument:
    blocks = (
        [{"kind": "paragraph", "text": f"p{i}", "style_name": "", "spans": []} for i in range(paragraphs)]
        + [{"kind": "heading", "text": f"h{i}", "style_name": "", "outline_level": 1, "spans": []} for i in range(headings)]
    )
    return FodtDocument({
        "format_id": "fodt",
        "odf_version": "1.3",
        "blocks": blocks,
        "table_count": tables,
        "list_count": lists,
        "warnings": [],
    })


# ── total_block_count ─────────────────────────────────────────────────────────

class TestTotalBlockCount:
    def test_empty_doc_zero(self):
        doc = _make_doc(0, 0)
        assert doc.total_block_count == 0

    def test_only_paragraphs(self):
        doc = _make_doc(5, 0)
        assert doc.total_block_count == 5

    def test_only_headings(self):
        doc = _make_doc(0, 3)
        assert doc.total_block_count == 3

    def test_mixed_blocks(self):
        doc = _make_doc(4, 2)
        assert doc.total_block_count == 6

    def test_single_paragraph(self):
        doc = _make_doc(1, 0)
        assert doc.total_block_count == 1


# ── heading_ratio ─────────────────────────────────────────────────────────────

class TestHeadingRatio:
    def test_empty_doc_ratio_zero(self):
        doc = _make_doc(0, 0)
        assert doc.heading_ratio == pytest.approx(0.0)

    def test_no_headings_ratio_zero(self):
        doc = _make_doc(5, 0)
        assert doc.heading_ratio == pytest.approx(0.0)

    def test_all_headings_ratio_one(self):
        doc = _make_doc(0, 4)
        assert doc.heading_ratio == pytest.approx(1.0)

    def test_half_headings(self):
        doc = _make_doc(2, 2)
        assert doc.heading_ratio == pytest.approx(0.5)

    def test_one_heading_four_paragraphs(self):
        doc = _make_doc(4, 1)
        assert doc.heading_ratio == pytest.approx(0.2)


# ── is_outline_heavy ──────────────────────────────────────────────────────────

class TestIsOutlineHeavy:
    def test_ratio_above_30_pct_is_heavy(self):
        # 4 headings / (4+8) total = 0.33 > 0.3
        doc = _make_doc(8, 4)
        assert doc.is_outline_heavy is True

    def test_ratio_below_30_pct_not_heavy(self):
        doc = _make_doc(8, 2)
        assert doc.is_outline_heavy is False

    def test_no_blocks_not_heavy(self):
        doc = _make_doc(0, 0)
        assert doc.is_outline_heavy is False

    def test_all_headings_is_heavy(self):
        doc = _make_doc(0, 5)
        assert doc.is_outline_heavy is True

    def test_exactly_30_pct_not_heavy(self):
        # 3/10 = 0.3 exactly — not > 0.3
        doc = _make_doc(7, 3)
        assert doc.is_outline_heavy is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_total_matches_paragraph_plus_heading(self):
        doc = _make_doc(5, 2)
        assert doc.total_block_count == doc.paragraph_count + doc.heading_count

    def test_heavy_implies_ratio_above_30(self):
        doc = _make_doc(3, 4)
        assert doc.is_outline_heavy is True
        assert doc.heading_ratio > 0.3

    def test_ratio_consistent_with_counts(self):
        doc = _make_doc(6, 2)
        assert doc.heading_ratio == pytest.approx(doc.heading_count / doc.total_block_count)
