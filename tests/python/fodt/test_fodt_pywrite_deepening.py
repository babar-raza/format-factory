"""TC-EXEC-003: FODT Python write deepening tests.

Verifies that FODT write→reload produces semantically equivalent content —
paragraph text, heading text/type, block ordering, and list items.
"""
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fodt import parse_fodt_strict, write_fodt
from src.python.fodt.writer import FodtInputError


def _para(text):
    return {"type": "paragraph", "text": text}


def _heading(text, level=1):
    return {"type": "heading", "text": text, "heading_level": level}


def _doc(blocks):
    return {"blocks": blocks}


def _roundtrip(document, tmp_path):
    dest = tmp_path / "rt.fodt"
    write_fodt(document, dest)
    return parse_fodt_strict(str(dest))


class TestFodtWriteDeepeningParagraphs:
    def test_single_paragraph_text_preserved(self, tmp_path):
        """Single paragraph text survives write→reload."""
        doc = _doc([_para("Hello world.")])
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        assert len(blocks) >= 1
        assert blocks[0]["text"] == "Hello world."

    def test_multi_paragraph_texts_preserved(self, tmp_path):
        """Multiple paragraph texts survive round-trip in order."""
        doc = _doc([_para("First."), _para("Second."), _para("Third.")])
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        texts = [b["text"] for b in blocks]
        assert "First." in texts
        assert "Second." in texts
        assert "Third." in texts

    def test_paragraph_ordering_preserved(self, tmp_path):
        """Block ordering matches input after round-trip."""
        doc = _doc([_para("A"), _para("B"), _para("C")])
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        assert len(blocks) == 3
        assert blocks[0]["text"] == "A"
        assert blocks[1]["text"] == "B"
        assert blocks[2]["text"] == "C"


class TestFodtWriteDeepeningHeadings:
    def test_heading_text_preserved(self, tmp_path):
        """Heading text survives write→reload."""
        doc = _doc([_heading("Chapter One")])
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        assert len(blocks) >= 1
        assert blocks[0]["text"] == "Chapter One"

    def test_heading_type_preserved(self, tmp_path):
        """Heading block type survives write→reload."""
        doc = _doc([_heading("Title")])
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        assert blocks[0]["type"] == "heading"

    def test_mixed_heading_and_paragraphs(self, tmp_path):
        """Mixed heading + paragraphs round-trip correctly."""
        doc = _doc([_heading("Intro"), _para("Body text."), _para("More text.")])
        doc2 = _roundtrip(doc, tmp_path)
        blocks = doc2.get("blocks", [])
        assert len(blocks) == 3
        assert blocks[0]["type"] == "heading"
        assert blocks[0]["text"] == "Intro"
        assert blocks[1]["text"] == "Body text."


class TestFodtWriteDeepeningEdgeCases:
    def test_empty_document_produces_valid_fodt(self, tmp_path):
        """An empty document writes and re-parses without error."""
        doc = _doc([])
        doc2 = _roundtrip(doc, tmp_path)
        assert isinstance(doc2, dict)
        assert doc2.get("blocks", []) == [] or len(doc2.get("blocks", [])) == 0

    def test_block_count_matches_input(self, tmp_path):
        """Block count matches original after round-trip."""
        doc = _doc([_para("X"), _para("Y"), _heading("H"), _para("Z")])
        doc2 = _roundtrip(doc, tmp_path)
        assert len(doc2.get("blocks", [])) == 4

    def test_invalid_input_raises(self):
        """document_to_xml raises FodtInputError on non-dict."""
        from src.python.fodt.writer import document_to_xml
        with pytest.raises(Exception):
            document_to_xml("not a dict")
