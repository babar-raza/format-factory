"""Tests for FODT export targets (HO-RC003-FODT-EXPORT, PQ-T2-007).

Verifies fodt_to_txt(), fodt_to_markdown(), fodt_to_html() produce correct output
from the FODT neutral model.

Parity target: .NET FodtTxtExporter, FodtMarkdownExporter, FodtHtmlExporter
Gap closure: GAP-INV-038
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODT_FIXTURE = _REPO / "tests" / "net" / "fodt" / "Fixtures" / "fodt-headings-and-list.fodt"
_FODT_MINIMAL = _REPO / "tests" / "net" / "fodt" / "Fixtures" / "fodt-minimal-roundtrip.fodt"

sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.exporters import fodt_to_html, fodt_to_markdown, fodt_to_txt


# --- Shared neutral model fixture ---

def _make_model(blocks):
    """Build a minimal neutral model from a list of block dicts."""
    content = [{"kind": "block", "data": b} for b in blocks]
    return {"content": content, "blocks": [], "lists": [], "tables": []}


# ===================================================================
# fodt_to_txt
# ===================================================================

class TestFodtToTxt:
    def test_accepts_neutral_model_dict(self):
        model = _make_model([
            {"type": "heading", "text": "Title", "heading_level": 1},
            {"type": "paragraph", "text": "Body text.", "heading_level": None},
        ])
        result = fodt_to_txt(model)
        assert isinstance(result, str)
        assert "Title" in result
        assert "Body text." in result

    def test_headings_and_paragraphs_separated_by_newline(self):
        model = _make_model([
            {"type": "heading", "text": "Heading", "heading_level": 1},
            {"type": "paragraph", "text": "Para", "heading_level": None},
        ])
        result = fodt_to_txt(model)
        assert result == "Heading\nPara"

    def test_list_items_prefixed(self):
        model = _make_model([
            {"type": "list_item", "text": "Item A", "heading_level": None},
            {"type": "list_item", "text": "Item B", "heading_level": None},
        ])
        result = fodt_to_txt(model)
        assert "- Item A" in result
        assert "- Item B" in result

    def test_empty_blocks_skipped(self):
        model = _make_model([
            {"type": "paragraph", "text": "  ", "heading_level": None},
            {"type": "paragraph", "text": "Real", "heading_level": None},
        ])
        result = fodt_to_txt(model)
        assert result == "Real"

    def test_accepts_file_path(self):
        if not _FODT_FIXTURE.exists():
            pytest.skip("FODT fixture not found")
        result = fodt_to_txt(_FODT_FIXTURE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_file_contains_expected_text(self):
        if not _FODT_FIXTURE.exists():
            pytest.skip("FODT fixture not found")
        result = fodt_to_txt(_FODT_FIXTURE)
        assert "Chapter One" in result


# ===================================================================
# fodt_to_markdown
# ===================================================================

class TestFodtToMarkdown:
    def test_heading_level_1(self):
        model = _make_model([{"type": "heading", "text": "Title", "heading_level": 1}])
        result = fodt_to_markdown(model)
        assert result == "# Title"

    def test_heading_level_2(self):
        model = _make_model([{"type": "heading", "text": "Sub", "heading_level": 2}])
        result = fodt_to_markdown(model)
        assert result == "## Sub"

    def test_heading_level_clamps_to_6(self):
        model = _make_model([{"type": "heading", "text": "Deep", "heading_level": 9}])
        result = fodt_to_markdown(model)
        assert result.startswith("######")

    def test_paragraph_is_plain_text(self):
        model = _make_model([{"type": "paragraph", "text": "A paragraph.", "heading_level": None}])
        result = fodt_to_markdown(model)
        assert result == "A paragraph."

    def test_list_item_prefixed_with_dash(self):
        model = _make_model([{"type": "list_item", "text": "Item", "heading_level": None}])
        result = fodt_to_markdown(model)
        assert result == "- Item"

    def test_parts_separated_by_double_newline(self):
        model = _make_model([
            {"type": "heading", "text": "H", "heading_level": 1},
            {"type": "paragraph", "text": "P", "heading_level": None},
        ])
        result = fodt_to_markdown(model)
        assert result == "# H\n\nP"

    def test_file_produces_markdown_headings(self):
        if not _FODT_FIXTURE.exists():
            pytest.skip("FODT fixture not found")
        result = fodt_to_markdown(_FODT_FIXTURE)
        assert "# Chapter One" in result or "#" in result


# ===================================================================
# fodt_to_html
# ===================================================================

class TestFodtToHtml:
    def test_heading_1_produces_h1(self):
        model = _make_model([{"type": "heading", "text": "Title", "heading_level": 1}])
        result = fodt_to_html(model)
        assert "<h1>Title</h1>" in result

    def test_heading_3_produces_h3(self):
        model = _make_model([{"type": "heading", "text": "Sub", "heading_level": 3}])
        result = fodt_to_html(model)
        assert "<h3>Sub</h3>" in result

    def test_paragraph_produces_p_tag(self):
        model = _make_model([{"type": "paragraph", "text": "Body.", "heading_level": None}])
        result = fodt_to_html(model)
        assert "<p>Body.</p>" in result

    def test_list_items_wrapped_in_ul(self):
        model = _make_model([
            {"type": "list_item", "text": "A", "heading_level": None},
            {"type": "list_item", "text": "B", "heading_level": None},
        ])
        result = fodt_to_html(model)
        assert "<ul>" in result
        assert "<li>A</li>" in result
        assert "<li>B</li>" in result

    def test_html_entities_escaped(self):
        model = _make_model([{"type": "paragraph", "text": "<b>bold</b>", "heading_level": None}])
        result = fodt_to_html(model)
        assert "<p>&lt;b&gt;bold&lt;/b&gt;</p>" in result
        assert "<b>bold</b>" not in result

    def test_list_items_flushed_before_heading(self):
        model = _make_model([
            {"type": "list_item", "text": "Item", "heading_level": None},
            {"type": "heading", "text": "Next", "heading_level": 2},
        ])
        result = fodt_to_html(model)
        ul_pos = result.index("<ul>")
        h2_pos = result.index("<h2>")
        assert ul_pos < h2_pos

    def test_file_produces_html(self):
        if not _FODT_FIXTURE.exists():
            pytest.skip("FODT fixture not found")
        result = fodt_to_html(_FODT_FIXTURE)
        assert "<h1>" in result or "<h2>" in result or "<p>" in result
