"""Sprint R1222 — FODT spec-parity deepening tests.

Tests spec-backed FODT functions mapped in test_spec_parity_fodt_proof.py:
  FODT-FACT-001: parse_fodt, parse_fodt_strict, write_fodt, document_to_xml
  FODT-FACT-002: document_text_content, document_paragraph_count, document_extract_headings
  FODT-FACT-003: document_hyperlink_count, document_footnote_count, document_paragraph_style_distribution
  FODT-FACT-004: document_table_summary, document_count_tables, document_table_cell_count
  FODT-FACT-005: document_list_stats, document_list_item_count, document_block_type_count
  FODT-FACT-006: document_section_summary, document_image_frame_list
  FODT-FACT-007: document_change_tracking_summary, document_stats
  FODT-FACT-015: document_extract_headings, document_heading_outline, document_heading_level_distribution
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    parse_fodt_strict,
    write_fodt,
    document_to_xml,
    document_stats,
    document_text_content,
    document_paragraph_count,
    document_extract_headings,
    document_heading_outline,
    document_heading_level_distribution,
    document_hyperlink_count,
    document_footnote_count,
    document_paragraph_style_distribution,
    document_table_summary,
    document_count_tables,
    document_table_cell_count,
    document_list_stats,
    document_list_item_count,
    document_block_type_count,
    document_section_summary,
    document_image_frame_list,
    document_change_tracking_summary,
    document_word_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_SAMPLES / "minimal-document.fodt")
_HEADINGS = str(_SAMPLES / "headings-and-paragraphs.fodt")
_LISTS = str(_SAMPLES / "list-basic.fodt")
_TABLES = str(_SAMPLES / "table-basic.fodt")


class TestFodtFactParse:
    """FODT-FACT-001: flat XML parse/write."""

    def test_parse_fodt_returns_dict(self):
        doc = parse_fodt(_MINIMAL)
        assert isinstance(doc, dict)

    def test_parse_fodt_strict_returns_dict(self):
        doc = parse_fodt_strict(_MINIMAL)
        assert isinstance(doc, dict)

    def test_document_to_xml_returns_str_or_bytes(self):
        doc = parse_fodt(_MINIMAL)
        xml = document_to_xml(doc)
        assert isinstance(xml, (str, bytes))

    def test_document_to_xml_has_office_namespace(self):
        doc = parse_fodt(_MINIMAL)
        xml = document_to_xml(doc)
        xml_str = xml if isinstance(xml, str) else xml.decode()
        assert "office" in xml_str

    def test_write_fodt_roundtrip(self, tmp_path):
        doc = parse_fodt(_MINIMAL)
        out = tmp_path / "roundtrip.fodt"
        write_fodt(doc, str(out))
        doc2 = parse_fodt(str(out))
        assert isinstance(doc2, dict)

    def test_headings_document_parses(self):
        doc = parse_fodt(_HEADINGS)
        assert isinstance(doc, dict)


class TestFodtFactTextContent:
    """FODT-FACT-002: text content and paragraph structure."""

    def test_document_text_content_returns_str(self):
        doc = parse_fodt(_HEADINGS)
        text = document_text_content(doc)
        assert isinstance(text, str)

    def test_document_text_content_non_empty(self):
        doc = parse_fodt(_HEADINGS)
        text = document_text_content(doc)
        assert len(text) > 0

    def test_document_paragraph_count_returns_int(self):
        doc = parse_fodt(_HEADINGS)
        count = document_paragraph_count(doc)
        assert isinstance(count, int)
        assert count >= 0

    def test_document_extract_headings_returns_list(self):
        doc = parse_fodt(_HEADINGS)
        headings = document_extract_headings(doc)
        assert isinstance(headings, list)

    def test_document_extract_headings_has_text(self):
        doc = parse_fodt(_HEADINGS)
        headings = document_extract_headings(doc)
        assert len(headings) >= 1
        for h in headings:
            assert "text" in h or isinstance(h, str)

    def test_document_heading_outline_returns_list(self):
        doc = parse_fodt(_HEADINGS)
        outline = document_heading_outline(doc)
        assert isinstance(outline, list)

    def test_document_heading_level_distribution_returns_dict(self):
        doc = parse_fodt(_HEADINGS)
        dist = document_heading_level_distribution(doc)
        assert isinstance(dist, dict)

    def test_document_word_count_returns_dict(self):
        doc = parse_fodt(_HEADINGS)
        wc = document_word_count(doc)
        assert isinstance(wc, dict)
        assert "total_words" in wc
        assert wc["total_words"] >= 0


class TestFodtFactInlineFormatting:
    """FODT-FACT-003: inline formatting and style distribution."""

    def test_document_hyperlink_count_returns_value(self):
        doc = parse_fodt(_MINIMAL)
        count = document_hyperlink_count(doc)
        # Returns int or dict with 'total' key
        if isinstance(count, dict):
            assert "total" in count
            assert count["total"] >= 0
        else:
            assert isinstance(count, int)
            assert count >= 0

    def test_document_footnote_count_returns_value(self):
        doc = parse_fodt(_MINIMAL)
        count = document_footnote_count(doc)
        # Returns int or dict with 'total' key
        if isinstance(count, dict):
            assert "total" in count
            assert count["total"] >= 0
        else:
            assert isinstance(count, int)
            assert count >= 0

    def test_document_paragraph_style_distribution_returns_dict(self):
        doc = parse_fodt(_HEADINGS)
        psd = document_paragraph_style_distribution(doc)
        assert isinstance(psd, dict)

    def test_paragraph_style_distribution_non_empty_for_headings_doc(self):
        doc = parse_fodt(_HEADINGS)
        psd = document_paragraph_style_distribution(doc)
        assert len(psd) >= 1


class TestFodtFactTables:
    """FODT-FACT-004: table structure."""

    def test_document_count_tables_returns_int(self):
        doc = parse_fodt(_TABLES)
        count = document_count_tables(doc)
        assert isinstance(count, int)
        assert count >= 0

    def test_document_stats_shows_table_count(self):
        doc = parse_fodt(_TABLES)
        stats = document_stats(doc)
        assert stats["table_count"] >= 1

    def test_document_table_summary_returns_list(self):
        doc = parse_fodt(_TABLES)
        summary = document_table_summary(doc)
        assert isinstance(summary, list)

    def test_document_table_cell_count_returns_value(self):
        doc = parse_fodt(_TABLES)
        count = document_table_cell_count(doc)
        # Returns int or dict with 'total_cells'
        if isinstance(count, dict):
            assert "total_cells" in count
            assert count["total_cells"] >= 0
        else:
            assert isinstance(count, int)
            assert count >= 0

    def test_document_no_tables_in_minimal(self):
        doc = parse_fodt(_MINIMAL)
        stats = document_stats(doc)
        assert stats["table_count"] == 0


class TestFodtFactLists:
    """FODT-FACT-005: list structure."""

    def test_document_list_stats_returns_dict(self):
        doc = parse_fodt(_LISTS)
        stats = document_list_stats(doc)
        assert isinstance(stats, dict)

    def test_document_list_item_count_returns_int(self):
        doc = parse_fodt(_LISTS)
        count = document_list_item_count(doc)
        assert isinstance(count, int)
        assert count >= 0

    def test_document_block_type_count_returns_dict(self):
        doc = parse_fodt(_HEADINGS)
        btc = document_block_type_count(doc)
        assert isinstance(btc, dict)

    def test_document_block_type_count_has_block_types(self):
        doc = parse_fodt(_HEADINGS)
        btc = document_block_type_count(doc)
        assert len(btc) >= 1


class TestFodtFactSections:
    """FODT-FACT-006: sections and image frames."""

    def test_document_section_summary_returns_value(self):
        doc = parse_fodt(_MINIMAL)
        sections = document_section_summary(doc)
        # Returns list or dict with 'section_count'
        assert isinstance(sections, (list, dict))

    def test_document_image_frame_list_returns_list(self):
        doc = parse_fodt(_MINIMAL)
        frames = document_image_frame_list(doc)
        assert isinstance(frames, list)

    def test_document_image_frame_list_minimal_empty(self):
        doc = parse_fodt(_MINIMAL)
        frames = document_image_frame_list(doc)
        # Minimal document has no images
        assert len(frames) == 0


class TestFodtFactChangeTracking:
    """FODT-FACT-007: change tracking."""

    def test_document_change_tracking_summary_returns_dict(self):
        doc = parse_fodt(_MINIMAL)
        cts = document_change_tracking_summary(doc)
        assert isinstance(cts, dict)

    def test_document_stats_block_count_non_negative(self):
        doc = parse_fodt(_HEADINGS)
        stats = document_stats(doc)
        assert stats["block_count"] >= 0

    def test_document_stats_heading_count(self):
        doc = parse_fodt(_HEADINGS)
        stats = document_stats(doc)
        assert stats["heading_count"] >= 1

    def test_document_stats_table_count_from_table_doc(self):
        doc = parse_fodt(_TABLES)
        stats = document_stats(doc)
        assert stats["table_count"] >= 1
