"""TC-EXEC-004: FODT semantic round-trip verification.

Deep field comparison after parse→write→reload cycle.
Verifies that block texts, types, ordering, and structure are fully
preserved through a complete round-trip.
"""
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fodt import parse_fodt_strict, write_fodt


def _roundtrip(document, tmp_path):
    dest = tmp_path / "semantic_rt.fodt"
    write_fodt(document, dest)
    return parse_fodt_strict(str(dest))


def _build_rich_document():
    """Build a synthetic document representative of real-world FODT content."""
    return {
        "blocks": [
            {"type": "heading", "text": "Executive Summary", "heading_level": 1},
            {"type": "paragraph", "text": "This is the first paragraph of the summary."},
            {"type": "paragraph", "text": "This is the second paragraph."},
            {"type": "heading", "text": "Details", "heading_level": 2},
            {"type": "paragraph", "text": "Detail paragraph one."},
            {"type": "paragraph", "text": "Detail paragraph two."},
        ]
    }


class TestFodtSemanticRoundtripBlocks:
    def test_paragraph_text_matches_exactly(self, tmp_path):
        """Paragraph text matches original exactly after round-trip."""
        doc = _build_rich_document()
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        texts = [b["text"] for b in blocks]
        assert "This is the first paragraph of the summary." in texts
        assert "This is the second paragraph." in texts

    def test_heading_text_matches_exactly(self, tmp_path):
        """Heading text matches original exactly after round-trip."""
        doc = _build_rich_document()
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        heading_texts = [b["text"] for b in blocks if b.get("type") == "heading"]
        assert "Executive Summary" in heading_texts
        assert "Details" in heading_texts

    def test_heading_type_survives(self, tmp_path):
        """Block type 'heading' is preserved after round-trip."""
        doc = _build_rich_document()
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        types = [b.get("type") for b in blocks]
        assert "heading" in types

    def test_paragraph_type_survives(self, tmp_path):
        """Block type 'paragraph' is preserved after round-trip."""
        doc = _build_rich_document()
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        types = [b.get("type") for b in blocks]
        assert "paragraph" in types


class TestFodtSemanticRoundtripOrdering:
    def test_block_ordering_preserved(self, tmp_path):
        """Block ordering matches input after round-trip."""
        doc = _build_rich_document()
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        assert len(blocks) == 6
        assert blocks[0]["text"] == "Executive Summary"
        assert blocks[1]["text"] == "This is the first paragraph of the summary."
        assert blocks[3]["text"] == "Details"

    def test_block_count_matches(self, tmp_path):
        """Block count matches original after round-trip."""
        doc = _build_rich_document()
        doc2 = _roundtrip(doc, tmp_path)
        assert len(doc2.get("blocks", [])) == len(doc["blocks"])


class TestFodtSemanticRoundtripEdgeCases:
    def test_empty_document_round_trip(self, tmp_path):
        """Empty document produces valid FODT and re-parses cleanly."""
        doc = {"blocks": []}
        doc2 = _roundtrip(doc, tmp_path)
        assert isinstance(doc2, dict)
        assert len(doc2.get("blocks", [])) == 0

    def test_single_paragraph_round_trip(self, tmp_path):
        """Single paragraph survives round-trip with correct text."""
        doc = {"blocks": [{"type": "paragraph", "text": "Only paragraph."}]}
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        assert len(blocks) == 1
        assert blocks[0]["text"] == "Only paragraph."
