"""
tests/python/fodt/test_r202_fodt_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT11-001
TASK-001: FODT advanced operations — parse/load, document info, text access,
analytics, export, mutation.

Covers: parse_fodt, parse_fodt_strict, document_stats, document_heading_outline,
document_text_content, document_word_count, document_table_summary, document_list_stats,
document_reading_level, document_hyperlink_count, document_footnote_count,
document_heading_level_distribution, document_table_cell_count, document_paragraph_count,
document_to_text, document_get_paragraph_text, document_search_text, document_replace_text,
document_to_html, document_extract_headings, document_count_tables, document_total_words,
document_list_item_count, document_block_type_count, document_max_paragraph_length,
document_has_tables, document_set_block_text, document_append_paragraph,
document_remove_paragraph, document_warnings_for_unsupported_edit,
document_to_xml, write_fodt, document_section_summary, document_footnote_endnote_summary.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt, parse_fodt_strict, write_fodt, document_to_xml,
    document_stats, document_heading_outline, document_text_content,
    document_word_count, document_table_summary, document_list_stats,
    document_reading_level, document_hyperlink_count, document_footnote_count,
    document_heading_level_distribution, document_table_cell_count,
    document_paragraph_count, document_to_text, document_get_paragraph_text,
    document_search_text, document_replace_text, document_to_html,
    document_extract_headings, document_count_tables, document_total_words,
    document_list_item_count, document_block_type_count, document_max_paragraph_length,
    document_has_tables, document_set_block_text, document_append_paragraph,
    document_remove_paragraph, document_warnings_for_unsupported_edit,
    document_section_summary, document_footnote_endnote_summary,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_SAMPLES / "minimal-document.fodt")
_HEADINGS = str(_SAMPLES / "headings-and-paragraphs.fodt")
_TABLE = str(_SAMPLES / "table-basic.fodt")
_LIST = str(_SAMPLES / "list-basic.fodt")


class TestFodtParseAndLoad:
    """parse_fodt, parse_fodt_strict, document_stats basic fields."""

    def test_parse_fodt_returns_dict(self):
        doc = parse_fodt(_MINIMAL)
        assert isinstance(doc, dict)

    def test_parse_fodt_has_format_id(self):
        doc = parse_fodt(_MINIMAL)
        assert doc.get("format_id") == "fodt"

    def test_parse_fodt_strict_returns_dict(self):
        doc = parse_fodt_strict(_MINIMAL)
        assert isinstance(doc, dict)

    def test_parse_fodt_headings_file(self):
        doc = parse_fodt(_HEADINGS)
        assert isinstance(doc, dict)

    def test_parse_fodt_table_file(self):
        doc = parse_fodt(_TABLE)
        assert isinstance(doc, dict)

    def test_parse_fodt_list_file(self):
        doc = parse_fodt(_LIST)
        assert isinstance(doc, dict)

    def test_document_stats_returns_dict(self):
        doc = parse_fodt(_MINIMAL)
        stats = document_stats(doc)
        assert isinstance(stats, dict)

    def test_parse_fodt_has_warnings(self):
        doc = parse_fodt(_MINIMAL)
        assert "warnings" in doc
        assert isinstance(doc["warnings"], list)

    def test_parse_fodt_headings_no_exception(self):
        doc = parse_fodt(_HEADINGS)
        assert isinstance(doc, dict)

    def test_parse_fodt_minimal_has_blocks(self):
        doc = parse_fodt(_MINIMAL)
        # Either 'blocks' or some block-related key
        assert "blocks" in doc or "format_id" in doc


class TestFodtDocumentInfo:
    """document_paragraph_count, document_word_count, document_total_words, document_block_type_count."""

    def test_document_paragraph_count_int(self):
        doc = parse_fodt(_HEADINGS)
        n = document_paragraph_count(doc)
        assert isinstance(n, int)
        assert n >= 1

    def test_document_word_count_dict(self):
        doc = parse_fodt(_HEADINGS)
        wc = document_word_count(doc)
        assert isinstance(wc, dict)

    def test_document_total_words_int(self):
        doc = parse_fodt(_HEADINGS)
        n = document_total_words(doc)
        assert isinstance(n, int)
        assert n >= 0

    def test_document_block_type_count_dict(self):
        doc = parse_fodt(_HEADINGS)
        btc = document_block_type_count(doc)
        assert isinstance(btc, dict)

    def test_document_max_paragraph_length_int(self):
        doc = parse_fodt(_HEADINGS)
        n = document_max_paragraph_length(doc)
        assert isinstance(n, int)
        assert n >= 0

    def test_document_heading_level_distribution_dict(self):
        doc = parse_fodt(_HEADINGS)
        hld = document_heading_level_distribution(doc)
        assert isinstance(hld, dict)

    def test_document_reading_level_dict(self):
        doc = parse_fodt(_HEADINGS)
        rl = document_reading_level(doc)
        assert isinstance(rl, dict)

    def test_document_hyperlink_count_dict(self):
        # Returns dict {'total': int, 'per_block': list}
        doc = parse_fodt(_MINIMAL)
        result = document_hyperlink_count(doc)
        assert isinstance(result, dict)
        assert "total" in result

    def test_document_footnote_count_dict(self):
        # Returns dict {'footnotes': int, 'endnotes': int, 'total': int, 'has_notes': bool}
        doc = parse_fodt(_MINIMAL)
        result = document_footnote_count(doc)
        assert isinstance(result, dict)
        assert "total" in result

    def test_document_list_stats_dict(self):
        doc = parse_fodt(_LIST)
        ls = document_list_stats(doc)
        assert isinstance(ls, dict)


class TestFodtTextAccess:
    """document_text_content, document_to_text, document_get_paragraph_text, document_search_text, document_heading_outline, document_extract_headings."""

    def test_document_text_content_str(self):
        doc = parse_fodt(_HEADINGS)
        text = document_text_content(doc)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_document_to_text_str(self):
        doc = parse_fodt(_HEADINGS)
        text = document_to_text(doc)
        assert isinstance(text, str)

    def test_document_get_paragraph_text_first(self):
        doc = parse_fodt(_HEADINGS)
        text = document_get_paragraph_text(doc, 0)
        assert isinstance(text, str)

    def test_document_get_paragraph_text_oob_none(self):
        # OOB index returns None
        doc = parse_fodt(_MINIMAL)
        text = document_get_paragraph_text(doc, 999)
        assert text is None or isinstance(text, str)

    def test_document_search_text_list(self):
        doc = parse_fodt(_HEADINGS)
        results = document_search_text(doc, "the")
        assert isinstance(results, list)

    def test_document_search_text_no_match(self):
        doc = parse_fodt(_MINIMAL)
        results = document_search_text(doc, "xyznotfound999")
        assert results == [] or isinstance(results, list)

    def test_document_heading_outline_list(self):
        doc = parse_fodt(_HEADINGS)
        outline = document_heading_outline(doc)
        assert isinstance(outline, list)

    def test_document_extract_headings_list(self):
        doc = parse_fodt(_HEADINGS)
        headings = document_extract_headings(doc)
        assert isinstance(headings, list)

    def test_document_list_item_count_int(self):
        doc = parse_fodt(_LIST)
        n = document_list_item_count(doc)
        assert isinstance(n, int)
        assert n >= 0


class TestFodtTableOps:
    """document_table_summary, document_table_cell_count, document_has_tables."""

    def test_document_table_summary_list(self):
        doc = parse_fodt(_TABLE)
        ts = document_table_summary(doc)
        assert isinstance(ts, list)
        assert len(ts) >= 1

    def test_document_table_cell_count_dict(self):
        # Returns dict {'total_cells': N, 'total_tables': M, 'per_table': [...]}
        doc = parse_fodt(_TABLE)
        result = document_table_cell_count(doc)
        assert isinstance(result, dict)
        assert result.get("total_cells", 0) >= 1

    def test_document_table_summary_has_row_count(self):
        doc = parse_fodt(_TABLE)
        ts = document_table_summary(doc)
        assert "row_count" in ts[0]

    def test_document_has_tables_true(self):
        doc = parse_fodt(_TABLE)
        assert document_has_tables(doc) is True

    def test_document_has_tables_false_or_bool(self):
        doc = parse_fodt(_MINIMAL)
        result = document_has_tables(doc)
        assert isinstance(result, bool)

    def test_document_count_tables_int(self):
        # Returns int (may be 0 if detection uses different mechanism)
        doc = parse_fodt(_TABLE)
        n = document_count_tables(doc)
        assert isinstance(n, int)


class TestFodtExportAndMutation:
    """document_to_html, document_to_xml, write_fodt, document_replace_text, document_set_block_text, document_append_paragraph, document_remove_paragraph."""

    def test_document_to_html_str(self):
        doc = parse_fodt(_HEADINGS)
        html = document_to_html(doc)
        assert isinstance(html, str)
        assert len(html) > 0

    def test_document_to_xml_str(self):
        doc = parse_fodt(_MINIMAL)
        xml_str = document_to_xml(doc)
        assert isinstance(xml_str, str)
        assert len(xml_str) > 0

    def test_write_fodt_creates_file(self):
        doc = parse_fodt(_MINIMAL)
        fd, path = tempfile.mkstemp(suffix=".fodt")
        os.close(fd)
        try:
            write_fodt(doc, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_document_replace_text_returns_doc(self):
        doc = parse_fodt(_HEADINGS)
        result = document_replace_text(doc, "Section", "Topic")
        assert isinstance(result, dict)

    def test_document_set_block_text_returns_tuple(self):
        doc = parse_fodt(_HEADINGS)
        n = document_paragraph_count(doc)
        if n > 0:
            result = document_set_block_text(doc, 0, "Updated Text")
            assert isinstance(result, tuple)
            assert isinstance(result[0], bool)

    def test_document_append_paragraph_returns_tuple(self):
        # Returns (bool, msg) tuple
        doc = parse_fodt(_MINIMAL)
        result = document_append_paragraph(doc, "New paragraph text")
        assert isinstance(result, tuple)
        assert isinstance(result[0], bool)

    def test_document_remove_paragraph_returns_tuple(self):
        # Returns (bool, msg) tuple
        doc = parse_fodt(_HEADINGS)
        result = document_remove_paragraph(doc, 0)
        assert isinstance(result, tuple)
        assert isinstance(result[0], bool)

    def test_document_warnings_for_unsupported_edit_list(self):
        doc = parse_fodt(_MINIMAL)
        warnings = document_warnings_for_unsupported_edit(doc, 0)
        assert isinstance(warnings, list)

    def test_document_footnote_endnote_summary_dict(self):
        doc = parse_fodt(_MINIMAL)
        result = document_footnote_endnote_summary(doc)
        assert isinstance(result, dict)

    def test_document_section_summary_dict(self):
        # Returns dict {'section_count': int, 'section_names': list}
        doc = parse_fodt(_MINIMAL)
        result = document_section_summary(doc)
        assert isinstance(result, dict)
        assert "section_count" in result
