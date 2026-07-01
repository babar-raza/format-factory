"""R562: FODT dimension properties — is_empty, has_content, is_single_block, has_headings.

Tests for FodtDocument dimension properties added in R562.
Spec refs: ODF-TEXT-FACT-PARAGRAPH.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.models import FodtDocument

SAMPLES = Path("samples/by-format/fodt")


def _make_doc(block_count=0, heading_count=0):
    """Build a minimal FodtDocument from a dict."""
    blocks = []
    for i in range(block_count - heading_count):
        blocks.append({"kind": "paragraph", "text": f"Para {i}", "style_name": ""})
    for i in range(heading_count):
        blocks.append({"kind": "heading", "text": f"Head {i}", "outline_level": 1, "style_name": ""})
    return FodtDocument({"format_id": "fodt", "blocks": blocks, "tables": [], "lists": []})


class TestIsEmpty:
    def test_no_blocks_is_empty(self):
        doc = _make_doc(block_count=0)
        assert doc.is_empty is True

    def test_one_block_not_empty(self):
        doc = _make_doc(block_count=1)
        assert doc.is_empty is False

    def test_multiple_blocks_not_empty(self):
        doc = _make_doc(block_count=3)
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(block_count=0)
        assert isinstance(doc.is_empty, bool)


class TestHasContent:
    def test_one_block_has_content(self):
        doc = _make_doc(block_count=1)
        assert doc.has_content is True

    def test_empty_no_content(self):
        doc = _make_doc(block_count=0)
        assert doc.has_content is False

    def test_has_content_type(self):
        doc = _make_doc(block_count=1)
        assert isinstance(doc.has_content, bool)


class TestIsSingleBlock:
    def test_one_block_is_single(self):
        doc = _make_doc(block_count=1)
        assert doc.is_single_block is True

    def test_zero_blocks_not_single(self):
        doc = _make_doc(block_count=0)
        assert doc.is_single_block is False

    def test_two_blocks_not_single(self):
        doc = _make_doc(block_count=2)
        assert doc.is_single_block is False

    def test_is_single_block_type(self):
        doc = _make_doc(block_count=1)
        assert isinstance(doc.is_single_block, bool)


class TestHasHeadings:
    def test_one_heading_has_headings(self):
        doc = _make_doc(block_count=1, heading_count=1)
        assert doc.has_headings is True

    def test_no_headings(self):
        doc = _make_doc(block_count=2, heading_count=0)
        assert doc.has_headings is False

    def test_mixed_content_headings(self):
        doc = _make_doc(block_count=3, heading_count=1)
        assert doc.has_headings is True

    def test_has_headings_type(self):
        doc = _make_doc(block_count=0)
        assert isinstance(doc.has_headings, bool)


class TestDimensionConsistency:
    def test_empty_and_has_content_exclusive(self):
        for n in [0, 1, 2, 5]:
            doc = _make_doc(block_count=n)
            assert doc.is_empty != doc.has_content

    def test_single_block_implies_has_content(self):
        doc = _make_doc(block_count=1)
        assert doc.is_single_block
        assert doc.has_content
        assert not doc.is_empty

    def test_from_file_minimal(self):
        doc = FodtDocument.from_file(str(SAMPLES / "minimal-document.fodt"))
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.has_content, bool)
        assert isinstance(doc.has_headings, bool)
