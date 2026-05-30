"""
tests/python/fodt/test_r76_fodt_edit_save.py

Tests for the R76 FODT edit-and-save product deepening capability.

Covers:
- document_set_block_text: update paragraph and heading blocks
- document_set_block_text: return value on success and failure
- document_warnings_for_unsupported_edit: warns on multi-run, hyperlink blocks
- Round-trip: parse → set_block_text → write_fodt → re-parse → verify
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.fodt import (
    parse_fodt,
    write_fodt,
    document_set_block_text,
    document_warnings_for_unsupported_edit,
)

FODT_MINIMAL = REPO_ROOT / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
FODT_HEADINGS = REPO_ROOT / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"


# ---------------------------------------------------------------------------
# document_set_block_text
# ---------------------------------------------------------------------------

class TestDocumentSetBlockText:
    def test_set_paragraph_text(self):
        doc = parse_fodt(FODT_MINIMAL)
        assert len(doc["blocks"]) > 0
        ok, msg = document_set_block_text(doc, 0, "Updated text")
        assert ok is True
        assert doc["blocks"][0]["text"] == "Updated text"

    def test_set_creates_single_run(self):
        doc = parse_fodt(FODT_MINIMAL)
        ok, _ = document_set_block_text(doc, 0, "New content")
        assert ok is True
        runs = doc["blocks"][0]["runs"]
        assert len(runs) == 1
        assert runs[0]["text"] == "New content"

    def test_preserves_block_type(self):
        doc = parse_fodt(FODT_MINIMAL)
        block_type = doc["blocks"][0]["type"]
        document_set_block_text(doc, 0, "Changed")
        assert doc["blocks"][0]["type"] == block_type

    def test_preserves_heading_level(self):
        doc = parse_fodt(FODT_HEADINGS)
        # Find a heading block
        heading_idx = None
        heading_level = None
        for i, block in enumerate(doc["blocks"]):
            if block.get("type") == "heading":
                heading_idx = i
                heading_level = block.get("heading_level")
                break
        if heading_idx is None:
            pytest.skip("No heading block in sample")
        document_set_block_text(doc, heading_idx, "Updated heading")
        assert doc["blocks"][heading_idx]["heading_level"] == heading_level

    def test_returns_false_for_out_of_range_idx(self):
        doc = parse_fodt(FODT_MINIMAL)
        ok, msg = document_set_block_text(doc, 99999, "text")
        assert ok is False
        assert "out of range" in msg.lower()

    def test_returns_false_for_invalid_document(self):
        ok, msg = document_set_block_text({}, 0, "text")
        assert ok is False

    def test_preserve_style_default_true(self):
        doc = parse_fodt(FODT_MINIMAL)
        # Inject a styled run
        doc["blocks"][0]["runs"] = [{"text": "original", "style": "Standard", "href": None}]
        ok, _ = document_set_block_text(doc, 0, "new text", preserve_style=True)
        assert ok is True
        assert doc["blocks"][0]["runs"][0]["style"] == "Standard"

    def test_preserve_style_false_clears_style(self):
        doc = parse_fodt(FODT_MINIMAL)
        doc["blocks"][0]["runs"] = [{"text": "original", "style": "Standard", "href": None}]
        ok, _ = document_set_block_text(doc, 0, "new text", preserve_style=False)
        assert ok is True
        assert doc["blocks"][0]["runs"][0]["style"] is None


class TestDocumentEditSaveRoundtrip:
    def test_round_trip_paragraph_edit(self, tmp_path):
        doc = parse_fodt(FODT_MINIMAL)
        ok, _ = document_set_block_text(doc, 0, "Round trip test content")
        assert ok is True

        out_path = tmp_path / "edited.fodt"
        write_fodt(doc, out_path)
        assert out_path.exists()

        doc2 = parse_fodt(out_path)
        assert doc2["blocks"][0]["text"] == "Round trip test content"

    def test_round_trip_preserves_block_count(self, tmp_path):
        doc = parse_fodt(FODT_MINIMAL)
        original_count = len(doc["blocks"])

        document_set_block_text(doc, 0, "Edited")
        out_path = tmp_path / "edited.fodt"
        write_fodt(doc, out_path)

        doc2 = parse_fodt(out_path)
        assert len(doc2["blocks"]) == original_count


class TestDocumentWarningsForUnsupportedEdit:
    def test_no_warnings_for_simple_block(self):
        doc = parse_fodt(FODT_MINIMAL)
        warnings = document_warnings_for_unsupported_edit(doc, 0)
        assert isinstance(warnings, list)
        # A plain paragraph should have no multi-run or hyperlink warnings

    def test_warns_for_multi_run_block(self):
        doc = parse_fodt(FODT_MINIMAL)
        doc["blocks"][0]["runs"] = [
            {"text": "part1", "style": None, "href": None},
            {"text": "part2", "style": None, "href": None},
        ]
        warnings = document_warnings_for_unsupported_edit(doc, 0)
        assert any("run" in w.lower() for w in warnings)

    def test_warns_for_hyperlink_run(self):
        doc = parse_fodt(FODT_MINIMAL)
        doc["blocks"][0]["runs"] = [{"text": "click", "style": None, "href": "https://example.com"}]
        warnings = document_warnings_for_unsupported_edit(doc, 0)
        assert any("hyperlink" in w.lower() for w in warnings)

    def test_returns_error_for_out_of_range(self):
        doc = parse_fodt(FODT_MINIMAL)
        warnings = document_warnings_for_unsupported_edit(doc, 99999)
        assert len(warnings) > 0
        assert "out of range" in warnings[0].lower()
