"""
test_r55_fodt_spans_ordering.py — Tests for TC-0057 (inline span preservation)
and TC-0060 (document ordering) for FODT Python writer.

R55 Train B:
  - TC-0057: inline text:span elements with style-name are preserved on round-trip.
  - TC-0060: document ordering (blocks, lists, tables interleaved) is preserved
             via the unified ``content`` sequence in the neutral model.

R55 Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.parser import parse_fodt_strict
from src.python.fodt.writer import document_to_xml, write_fodt

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
}


def _fodt_xml(body_inner: str, version: str = "1.3") -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document
          xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
          xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
          xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
          office:version="{version}"
          office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">
          <office:body>
            <office:text>
              {body_inner}
            </office:text>
          </office:body>
        </office:document>
    """)


def _write_and_parse(doc: dict, tmp_path: Path) -> dict:
    out = tmp_path / "out.fodt"
    write_fodt(doc, out)
    return parse_fodt_strict(out)


def _parse_from_string(xml_str: str, tmp_path: Path) -> dict:
    f = tmp_path / "input.fodt"
    f.write_text(xml_str, encoding="utf-8")
    return parse_fodt_strict(f)


# ===========================================================================
# TC-0057: Inline Span Preservation
# ===========================================================================

class TestInlineSpanCapture:
    """Parser captures text:span runs with style-name."""

    def test_styled_span_captured_in_runs(self, tmp_path):
        """A text:span with style-name appears in block['runs']."""
        xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            'plain '
            '<text:span text:style-name="Bold">bold text</text:span>'
            ' after</text:p>'
        )
        doc = _parse_from_string(xml, tmp_path)
        assert doc["blocks"], "No blocks parsed"
        block = doc["blocks"][0]
        assert "runs" in block
        runs = block["runs"]
        # Find the styled run
        styled = [r for r in runs if r.get("style") == "Bold"]
        assert styled, f"No styled run found in runs: {runs}"
        assert styled[0]["text"] == "bold text"

    def test_plain_text_run_has_no_style(self, tmp_path):
        """Plain text segments produce runs with style=None."""
        xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            'hello world</text:p>'
        )
        doc = _parse_from_string(xml, tmp_path)
        block = doc["blocks"][0]
        runs = block.get("runs", [])
        # All runs should have style=None
        for r in runs:
            assert r["style"] is None, f"Expected no style, got {r['style']}"

    def test_multiple_spans_captured(self, tmp_path):
        """Multiple spans in a paragraph produce multiple styled runs."""
        xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<text:span text:style-name="S1">first</text:span>'
            '<text:span text:style-name="S2">second</text:span>'
            '</text:p>'
        )
        doc = _parse_from_string(xml, tmp_path)
        block = doc["blocks"][0]
        runs = block["runs"]
        styled = [r for r in runs if r.get("style")]
        assert len(styled) == 2
        assert styled[0]["style"] == "S1"
        assert styled[1]["style"] == "S2"

    def test_text_field_preserved_as_combined_text(self, tmp_path):
        """block['text'] is still the full plain text concatenation."""
        xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            'pre '
            '<text:span text:style-name="I">italic</text:span>'
            ' post</text:p>'
        )
        doc = _parse_from_string(xml, tmp_path)
        block = doc["blocks"][0]
        # text is the full concatenation for backward compat
        assert "italic" in block["text"]
        assert "pre" in block["text"]
        assert "post" in block["text"]


class TestInlineSpanRoundTrip:
    """Inline spans survive parse → write → parse round-trip."""

    def test_span_roundtrip_preserves_style_name(self, tmp_path):
        """A styled span survives a full round-trip."""
        input_xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            'intro '
            '<text:span text:style-name="BoldStyle">bold</text:span>'
            ' outro</text:p>'
        )
        doc = _parse_from_string(input_xml, tmp_path)
        out_xml = document_to_xml(doc)
        root = ET.fromstring(out_xml)
        spans = root.findall(".//text:span", _NS)
        assert spans, "No text:span elements in round-tripped XML"
        assert spans[0].get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name") == "BoldStyle"
        assert spans[0].text == "bold"

    def test_span_roundtrip_preserves_plain_text_context(self, tmp_path):
        """Plain text before and after a span is preserved."""
        input_xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            'before '
            '<text:span text:style-name="X">middle</text:span>'
            ' after</text:p>'
        )
        doc = _parse_from_string(input_xml, tmp_path)
        out_xml = document_to_xml(doc)
        assert "before" in out_xml
        assert "middle" in out_xml
        assert "after" in out_xml

    def test_multiple_spans_roundtrip(self, tmp_path):
        """Multiple styled spans in one paragraph survive round-trip."""
        input_xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<text:span text:style-name="Bold">bold</text:span>'
            ' and '
            '<text:span text:style-name="Italic">italic</text:span>'
            '</text:p>'
        )
        doc = _parse_from_string(input_xml, tmp_path)
        out_xml = document_to_xml(doc)
        root = ET.fromstring(out_xml)
        spans = root.findall(".//text:span", _NS)
        assert len(spans) == 2
        styles = {s.get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name") for s in spans}
        assert "Bold" in styles
        assert "Italic" in styles

    def test_parse_write_parse_span_text_preserved(self, tmp_path):
        """Full parse→write→parse: the span text is recoverable from reloaded doc."""
        input_xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            'plain '
            '<text:span text:style-name="Emph">emphasis</text:span>'
            '</text:p>'
        )
        doc1 = _parse_from_string(input_xml, tmp_path)
        out = tmp_path / "roundtrip.fodt"
        write_fodt(doc1, out)
        doc2 = parse_fodt_strict(out)
        # The text "emphasis" should be recoverable from the re-parsed doc
        assert any("emphasis" in b.get("text", "") for b in doc2["blocks"])

    def test_heading_with_span_roundtrip(self, tmp_path):
        """A heading block with a styled span is preserved correctly."""
        input_xml = _fodt_xml(
            '<text:h xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' text:outline-level="1">'
            'Heading '
            '<text:span text:style-name="Emph">styled</text:span>'
            '</text:h>'
        )
        doc = _parse_from_string(input_xml, tmp_path)
        assert doc["blocks"][0]["type"] == "heading"
        out_xml = document_to_xml(doc)
        root = ET.fromstring(out_xml)
        spans = root.findall(".//text:span", _NS)
        assert spans, "No span in heading roundtrip"
        assert spans[0].text == "styled"


# ===========================================================================
# TC-0060: Document Ordering
# ===========================================================================

class TestDocumentOrdering:
    """content sequence preserves document order of blocks, lists, tables."""

    def test_parser_produces_content_key(self, tmp_path):
        """parse_fodt_strict returns a 'content' key in the result."""
        xml = _fodt_xml('<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Hello</text:p>')
        doc = _parse_from_string(xml, tmp_path)
        assert "content" in doc, "Parser must produce 'content' key (R55 TC-0060)"

    def test_content_reflects_insertion_order(self, tmp_path):
        """A paragraph followed by a list: content order is [block, list]."""
        xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            '        xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0">'
            'First paragraph</text:p>'
            '<text:list xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<text:list-item><text:p>Item 1</text:p></text:list-item>'
            '</text:list>'
        )
        doc = _parse_from_string(xml, tmp_path)
        assert "content" in doc
        kinds = [item["kind"] for item in doc["content"]]
        assert kinds == ["block", "list"], f"Expected [block, list], got {kinds}"

    def test_writer_uses_content_for_ordering(self, tmp_path):
        """When content is present, writer emits elements in content order."""
        xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Para A</text:p>'
            '<text:list xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<text:list-item><text:p>List item</text:p></text:list-item>'
            '</text:list>'
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Para B</text:p>'
        )
        doc = _parse_from_string(xml, tmp_path)
        out_xml = document_to_xml(doc)
        # Para A should appear before list, which should appear before Para B
        pos_a = out_xml.find("Para A")
        pos_list = out_xml.find("List item")
        pos_b = out_xml.find("Para B")
        assert pos_a < pos_list < pos_b, (
            f"Document order not preserved: Para A at {pos_a}, "
            f"List item at {pos_list}, Para B at {pos_b}"
        )

    def test_table_between_paragraphs_preserved(self, tmp_path):
        """A table between two paragraphs is emitted in correct position."""
        xml = _fodt_xml(
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Before</text:p>'
            '<table:table xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"'
            '             xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            '             table:name="T1">'
            '<table:table-row><table:table-cell><text:p>Cell</text:p></table:table-cell></table:table-row>'
            '</table:table>'
            '<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">After</text:p>'
        )
        doc = _parse_from_string(xml, tmp_path)
        out_xml = document_to_xml(doc)
        pos_before = out_xml.find("Before")
        pos_cell = out_xml.find("Cell")
        pos_after = out_xml.find("After")
        assert pos_before < pos_cell < pos_after

    def test_legacy_document_without_content_key_still_works(self):
        """A document dict without 'content' key still serializes correctly."""
        doc = {
            "blocks": [{"type": "paragraph", "text": "hello", "heading_level": None}],
            "lists": [],
            "tables": [],
            "odf_version_attr": "1.3",
        }
        out_xml = document_to_xml(doc)
        assert "hello" in out_xml
