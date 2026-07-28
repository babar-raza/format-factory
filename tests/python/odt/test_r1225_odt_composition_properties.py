"""R1225: ODT document composition properties — is_heading_heavy, is_content_rich, heading_ratio.

Tests for OdtModelDocument composition analysis properties added in R1225.
Spec refs: SAL-ODT-01067 (office:document text structure).
"""

from __future__ import annotations

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.models import OdtModelDocument, OdtDoc

SAMPLES = Path("samples/by-format/odt/valid")


def _make_doc(paragraph_count: int = 0, heading_count: int = 0) -> OdtModelDocument:
    """Build a minimal OdtModelDocument from stub data."""
    paragraphs = [types.SimpleNamespace(text=f"Para {i}") for i in range(paragraph_count)]
    headings = [types.SimpleNamespace(text=f"Head {i}") for i in range(heading_count)]
    return OdtModelDocument(types.SimpleNamespace(
        paragraphs=paragraphs,
        headings=headings,
        path="test.odt",
    ))


class TestIsHeadingHeavy:
    def test_no_content_not_heading_heavy(self):
        doc = _make_doc(paragraph_count=0, heading_count=0)
        assert doc.is_heading_heavy is False

    def test_equal_not_heading_heavy(self):
        doc = _make_doc(paragraph_count=3, heading_count=3)
        assert doc.is_heading_heavy is False

    def test_more_headings_is_heavy(self):
        doc = _make_doc(paragraph_count=2, heading_count=3)
        assert doc.is_heading_heavy is True

    def test_more_paragraphs_not_heavy(self):
        doc = _make_doc(paragraph_count=10, heading_count=2)
        assert doc.is_heading_heavy is False

    def test_zero_paragraphs_with_headings_is_heavy(self):
        doc = _make_doc(paragraph_count=0, heading_count=1)
        assert doc.is_heading_heavy is True

    def test_returns_bool(self):
        doc = _make_doc(paragraph_count=1, heading_count=0)
        assert isinstance(doc.is_heading_heavy, bool)

    def test_from_file(self):
        for p in sorted(SAMPLES.glob("*.odt"))[:2]:
            doc = OdtModelDocument.from_file(p)
            assert isinstance(doc.is_heading_heavy, bool)


class TestIsContentRich:
    def test_empty_not_rich(self):
        doc = _make_doc(paragraph_count=0, heading_count=0)
        assert doc.is_content_rich is False

    def test_ten_blocks_not_rich(self):
        """Exactly 10 blocks — not rich (threshold is > 10)."""
        doc = _make_doc(paragraph_count=7, heading_count=3)
        assert doc.is_content_rich is False

    def test_eleven_blocks_is_rich(self):
        doc = _make_doc(paragraph_count=8, heading_count=3)
        assert doc.is_content_rich is True

    def test_many_paragraphs_is_rich(self):
        doc = _make_doc(paragraph_count=20, heading_count=0)
        assert doc.is_content_rich is True

    def test_returns_bool(self):
        doc = _make_doc(paragraph_count=5, heading_count=0)
        assert isinstance(doc.is_content_rich, bool)

    def test_from_file(self):
        for p in sorted(SAMPLES.glob("*.odt"))[:2]:
            doc = OdtModelDocument.from_file(p)
            assert isinstance(doc.is_content_rich, bool)


class TestHeadingRatio:
    def test_empty_returns_zero(self):
        doc = _make_doc(paragraph_count=0, heading_count=0)
        assert doc.heading_ratio == pytest.approx(0.0)

    def test_all_headings_ratio_one(self):
        doc = _make_doc(paragraph_count=0, heading_count=5)
        assert doc.heading_ratio == pytest.approx(1.0)

    def test_no_headings_ratio_zero(self):
        doc = _make_doc(paragraph_count=5, heading_count=0)
        assert doc.heading_ratio == pytest.approx(0.0)

    def test_half_headings_ratio_half(self):
        doc = _make_doc(paragraph_count=3, heading_count=3)
        assert doc.heading_ratio == pytest.approx(0.5)

    def test_one_in_four_is_quarter(self):
        doc = _make_doc(paragraph_count=3, heading_count=1)
        assert doc.heading_ratio == pytest.approx(0.25)

    def test_returns_float(self):
        doc = _make_doc(paragraph_count=2, heading_count=1)
        assert isinstance(doc.heading_ratio, float)

    def test_ratio_between_zero_and_one(self):
        doc = _make_doc(paragraph_count=5, heading_count=2)
        assert 0.0 <= doc.heading_ratio <= 1.0

    def test_consistent_with_block_count(self):
        doc = _make_doc(paragraph_count=4, heading_count=2)
        assert doc.heading_ratio == pytest.approx(doc.heading_count / doc.total_block_count)

    def test_from_file(self):
        for p in sorted(SAMPLES.glob("*.odt"))[:2]:
            doc = OdtModelDocument.from_file(p)
            assert 0.0 <= doc.heading_ratio <= 1.0

    def test_odtdoc_alias_works(self):
        doc = OdtDoc(types.SimpleNamespace(
            paragraphs=[types.SimpleNamespace(text="p")],
            headings=[],
            path="test.odt",
        ))
        assert doc.heading_ratio == pytest.approx(0.0)
