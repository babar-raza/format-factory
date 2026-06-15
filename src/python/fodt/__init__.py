"""
format-factory-fodt -- Python FOSS parser/writer for OpenDocument Flat Text (FODT).

Public API:
    parse_fodt(file_path)              -- streaming parser, never raises
    parse_fodt_strict(file_path)       -- raises FodtError subclasses on failure
    write_fodt(document, path)         -- serialize neutral model document to FODT file
    document_to_xml(document)          -- serialize neutral model document to XML string
    document_stats(document)           -- return document-level statistics dict (R57/R58)
    document_heading_outline(document) -- ordered heading list for TOC (R59)
    document_text_content(document)    -- full text extraction as single string (R59)
    document_word_count(document)      -- approximate word count breakdown (R60)
    document_table_summary(document)   -- compact summary of all tables (R60)
    document_list_stats(document)      -- list count, items, depth statistics (R61)
    document_reading_level(document)   -- estimated reading level metrics (R61)
    document_hyperlink_count(document) -- count hyperlinks in document (R62)
    document_footnote_count(document)  -- count footnotes/endnotes (R62)
    document_table_cell_span_summary(document) -- colspan/rowspan stats (R64)
    document_text_field_warnings(document)     -- text field warnings (R64)
    document_footnote_endnote_summary(document) -- footnote/endnote/inline summary (R65)
    document_image_frame_list(document)         -- image frame inventory (R65)
    document_section_summary(document)          -- section inventory (R66)
    document_change_tracking_summary(document)  -- change tracking summary (R66)
    document_paragraph_style_distribution(doc)  -- paragraph style counts (R75)
    document_language_list(document)            -- language codes in document (R75)
    document_set_block_text(doc, idx, text)     -- edit a paragraph/heading block (R76)
    document_warnings_for_unsupported_edit(doc, idx) -- edit safety warnings (R76)

License: Apache-2.0
Package: format-factory-fodt v0.1.0
Gate history: Gates 1-9 PASSED (2026-05-08); Gate 10 Phase 4 code-complete (2026-05-09)
R46 MT6: write_fodt / document_to_xml added (alpha-foss-preview write capability)
R57/R58: document_stats() exposed in public API
R61: document_list_stats, document_reading_level added
R62: document_hyperlink_count, document_footnote_count added
R63: all 9 document APIs exported at package level (IV-R62-003 repair)
"""

from .parser import parse_fodt, parse_fodt_strict
from .writer import write_fodt, document_to_xml
from .neutral_model import (
    document_stats,
    document_heading_outline,
    document_text_content,
    document_word_count,
    document_table_summary,
    document_list_stats,
    document_reading_level,
    document_hyperlink_count,
    document_footnote_count,
    document_heading_level_distribution,
    document_table_cell_count,
    document_table_cell_span_summary,
    document_text_field_warnings,
    document_footnote_endnote_summary,
    document_image_frame_list,
    document_section_summary,
    document_change_tracking_summary,
    document_paragraph_style_distribution,
    document_language_list,
    document_set_block_text,
    document_warnings_for_unsupported_edit,
    document_append_paragraph,
    document_remove_paragraph,
    document_paragraph_count,
    document_to_text,
    document_get_paragraph_text,
    document_search_text,
    document_replace_text,
    document_to_html,
    document_extract_headings,
    document_count_tables,
    document_total_words,
    document_list_item_count,
    document_block_type_count,
    document_max_paragraph_length,
    document_has_tables,
    document_paragraph_texts,
    document_heading_texts,
    document_table_row_count,
    document_empty_paragraph_count,
    fodt_total_block_count,
)
from .exceptions import FodtError, FodtInputError, FodtSizeError, FodtParseError
from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION, MAX_FILE_BYTES

__version__ = PACKAGE_VERSION
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_fodt",
    "parse_fodt_strict",
    "write_fodt",
    "document_to_xml",
    "document_stats",
    "document_heading_outline",
    "document_text_content",
    "document_word_count",
    "document_table_summary",
    "document_list_stats",
    "document_reading_level",
    "document_hyperlink_count",
    "document_footnote_count",
    "document_heading_level_distribution",
    "document_table_cell_count",
    "document_table_cell_span_summary",
    "document_text_field_warnings",
    "document_footnote_endnote_summary",
    "document_image_frame_list",
    "document_section_summary",
    "document_change_tracking_summary",
    "document_paragraph_style_distribution",
    "document_language_list",
    "document_set_block_text",
    "document_warnings_for_unsupported_edit",
    "document_append_paragraph",
    "document_remove_paragraph",
    "document_paragraph_count",
    "document_to_text",
    "document_get_paragraph_text",
    "document_search_text",
    "document_replace_text",
    "document_to_html",
    "document_extract_headings",
    "document_count_tables",
    "document_total_words",
    "document_list_item_count",
    "document_block_type_count",
    "document_max_paragraph_length",
    "document_has_tables",
    "document_paragraph_texts",
    "document_heading_texts",
    "document_table_row_count",
    "document_empty_paragraph_count",
    "fodt_total_block_count",
    "FodtError",
    "FodtInputError",
    "FodtSizeError",
    "FodtParseError",
    "FORMAT_ID",
    "SPEC_VERSION",
    "PACKAGE_VERSION",
    "MAX_FILE_BYTES",
]
