"""
tests/python/fodt/test_r77_fodt_paragraph_management.py

R77 Train J — FODT paragraph management product depth:
- document_append_paragraph
- document_remove_paragraph
- document_paragraph_count

R79 Train G: updated fixtures to use root-level doc["blocks"]
(GAP-FODT-STRUCT-001 repaired — APIs now consistent with parser/writer).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.fodt import (
    document_append_paragraph,
    document_remove_paragraph,
    document_paragraph_count,
)


def _minimal_document(block_texts: list[str]) -> dict:
    """Build a minimal document dict with paragraph blocks (root-level blocks per parser)."""
    return {
        "blocks": [
            {"type": "paragraph", "runs": [{"text": t}], "auto_updatable": False}
            for t in block_texts
        ]
    }


class TestDocumentAppendParagraph:
    def test_append_to_empty_document(self):
        doc = {"blocks": []}
        ok, msg = document_append_paragraph(doc, "Hello world")
        assert ok
        assert len(doc["blocks"]) == 1
        assert doc["blocks"][0]["runs"][0]["text"] == "Hello world"

    def test_append_adds_to_end(self):
        doc = _minimal_document(["First"])
        ok, msg = document_append_paragraph(doc, "Second")
        assert ok
        assert doc["blocks"][-1]["runs"][0]["text"] == "Second"

    def test_append_with_style(self):
        doc = {"blocks": []}
        ok, msg = document_append_paragraph(doc, "Title", style="Heading 1")
        assert ok
        assert doc["blocks"][0].get("style") == "Heading 1"

    def test_append_without_style_has_no_style_key_or_none(self):
        doc = {"blocks": []}
        ok, msg = document_append_paragraph(doc, "Plain")
        assert ok
        block = doc["blocks"][0]
        assert block.get("style") is None

    def test_append_none_text_fails(self):
        doc = {"blocks": []}
        ok, msg = document_append_paragraph(doc, None)
        assert not ok

    def test_append_multiple_paragraphs(self):
        doc = {"blocks": []}
        for i in range(5):
            document_append_paragraph(doc, f"Para {i}")
        assert len(doc["blocks"]) == 5

    def test_append_empty_string_succeeds(self):
        doc = {"blocks": []}
        ok, msg = document_append_paragraph(doc, "")
        assert ok

    def test_append_sets_auto_updatable_false(self):
        doc = {"blocks": []}
        document_append_paragraph(doc, "Test")
        block = doc["blocks"][0]
        assert block.get("auto_updatable") is False


class TestDocumentRemoveParagraph:
    def test_remove_only_paragraph_when_one_block(self):
        doc = _minimal_document(["Solo"])
        ok, msg = document_remove_paragraph(doc, 0)
        assert ok
        assert len(doc["blocks"]) == 0

    def test_remove_first_paragraph(self):
        doc = _minimal_document(["A", "B", "C"])
        ok, _ = document_remove_paragraph(doc, 0)
        assert ok
        assert doc["blocks"][0]["runs"][0]["text"] == "B"

    def test_remove_last_paragraph(self):
        doc = _minimal_document(["A", "B"])
        ok, _ = document_remove_paragraph(doc, 1)
        assert ok
        assert len(doc["blocks"]) == 1

    def test_remove_out_of_range_index_fails(self):
        doc = _minimal_document(["Only"])
        ok, msg = document_remove_paragraph(doc, 5)
        assert not ok
        assert "out of range" in msg

    def test_remove_negative_index_fails(self):
        doc = _minimal_document(["A", "B"])
        ok, msg = document_remove_paragraph(doc, -1)
        assert not ok

    def test_remove_table_block_fails(self):
        doc = {
            "blocks": [
                {"type": "table", "rows": []},
            ]
        }
        ok, msg = document_remove_paragraph(doc, 0)
        assert not ok
        assert "table" in msg.lower()

    def test_remove_includes_preview_in_message(self):
        doc = _minimal_document(["Preview text here"])
        ok, msg = document_remove_paragraph(doc, 0)
        assert ok
        assert "Preview" in msg


class TestDocumentParagraphCount:
    def test_count_zero_for_empty_document(self):
        doc = {"blocks": []}
        assert document_paragraph_count(doc) == 0

    def test_count_paragraphs_only(self):
        doc = {
            "blocks": [
                {"type": "paragraph", "runs": [{"text": "A"}]},
                {"type": "table", "rows": []},
                {"type": "paragraph", "runs": [{"text": "B"}]},
            ]
        }
        assert document_paragraph_count(doc) == 2

    def test_count_all_paragraphs(self):
        doc = _minimal_document(["A", "B", "C", "D"])
        assert document_paragraph_count(doc) == 4

    def test_count_reflects_append(self):
        doc = _minimal_document(["A"])
        assert document_paragraph_count(doc) == 1
        document_append_paragraph(doc, "B")
        assert document_paragraph_count(doc) == 2

    def test_count_reflects_remove(self):
        doc = _minimal_document(["A", "B"])
        assert document_paragraph_count(doc) == 2
        document_remove_paragraph(doc, 0)
        assert document_paragraph_count(doc) == 1
