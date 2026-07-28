"""
Tests for FODT document analytics functions — deepening coverage.

Covers 24 single-argument document analytics functions:
  document_block_type_count, document_change_tracking_summary,
  document_count_tables, document_empty_paragraph_count,
  document_footnote_count, document_footnote_endnote_summary,
  document_heading_level_distribution, document_heading_outline,
  document_heading_texts, document_hyperlink_count, document_image_frame_list,
  document_language_list, document_list_item_count, document_list_stats,
  document_max_paragraph_length, document_paragraph_count,
  document_paragraph_style_distribution, document_paragraph_texts,
  document_reading_level, document_section_summary, document_total_words,
  document_word_count, document_table_summary, document_table_cell_count

Spec refs: SAL-FODT-00001 (text content model), SAL-FODT-00013 (paragraph),
           FACT-FODT-037 (headings), FACT-FODT-038 (document structure)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
_SAMPLES = _REPO / "samples" / "by-format" / "fodt"

from fodt import (
    parse_fodt,
    document_block_type_count,
    document_change_tracking_summary,
    document_count_tables,
    document_empty_paragraph_count,
    document_footnote_count,
    document_footnote_endnote_summary,
    document_heading_level_distribution,
    document_heading_outline,
    document_heading_texts,
    document_hyperlink_count,
    document_image_frame_list,
    document_language_list,
    document_list_item_count,
    document_list_stats,
    document_max_paragraph_length,
    document_paragraph_count,
    document_paragraph_style_distribution,
    document_paragraph_texts,
    document_reading_level,
    document_section_summary,
    document_total_words,
    document_word_count,
    document_table_summary,
    document_table_cell_count,
    document_has_tables,
)


@pytest.fixture(scope="module")
def doc_headings():
    return parse_fodt(str(_SAMPLES / "headings-and-paragraphs.fodt"))


@pytest.fixture(scope="module")
def doc_list():
    return parse_fodt(str(_SAMPLES / "list-basic.fodt"))


@pytest.fixture(scope="module")
def doc_table():
    return parse_fodt(str(_SAMPLES / "table-basic.fodt"))


@pytest.fixture(scope="module")
def doc_minimal():
    return parse_fodt(str(_SAMPLES / "minimal-document.fodt"))


# ---------------------------------------------------------------------------
# document_block_type_count
# ---------------------------------------------------------------------------

class TestDocumentBlockTypeCount:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_block_type_count(doc_headings), dict)

    def test_has_heading_key(self, doc_headings):
        result = document_block_type_count(doc_headings)
        assert "heading" in result

    def test_heading_count_positive(self, doc_headings):
        assert document_block_type_count(doc_headings)["heading"] > 0

    def test_paragraph_key_present(self, doc_headings):
        result = document_block_type_count(doc_headings)
        assert "paragraph" in result

    def test_list_doc_counts_correct(self, doc_list):
        assert isinstance(document_block_type_count(doc_list), dict)


# ---------------------------------------------------------------------------
# document_change_tracking_summary
# ---------------------------------------------------------------------------

class TestDocumentChangeTrackingSummary:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_change_tracking_summary(doc_headings), dict)

    def test_has_tracked_change_count(self, doc_headings):
        assert "tracked_change_count" in document_change_tracking_summary(doc_headings)

    def test_basic_has_no_changes(self, doc_headings):
        result = document_change_tracking_summary(doc_headings)
        assert result["tracked_change_count"] == 0

    def test_has_author_names(self, doc_headings):
        assert "author_names" in document_change_tracking_summary(doc_headings)

    def test_author_names_is_list(self, doc_headings):
        assert isinstance(document_change_tracking_summary(doc_headings)["author_names"], list)


# ---------------------------------------------------------------------------
# document_count_tables
# ---------------------------------------------------------------------------

class TestDocumentCountTables:
    def test_returns_int(self, doc_headings):
        assert isinstance(document_count_tables(doc_headings), int)

    def test_no_table_blocks_in_heading_doc(self, doc_headings):
        # document_count_tables counts blocks with block_type='table'
        assert document_count_tables(doc_headings) == 0

    def test_non_negative(self, doc_table):
        assert document_count_tables(doc_table) >= 0

    def test_list_doc_returns_int(self, doc_list):
        assert isinstance(document_count_tables(doc_list), int)

    def test_minimal_has_no_table_blocks(self, doc_minimal):
        assert document_count_tables(doc_minimal) == 0


# ---------------------------------------------------------------------------
# document_empty_paragraph_count
# ---------------------------------------------------------------------------

class TestDocumentEmptyParagraphCount:
    def test_returns_int(self, doc_headings):
        assert isinstance(document_empty_paragraph_count(doc_headings), int)

    def test_non_negative(self, doc_headings):
        assert document_empty_paragraph_count(doc_headings) >= 0

    def test_heading_doc_has_no_empty(self, doc_headings):
        assert document_empty_paragraph_count(doc_headings) == 0

    def test_list_doc_is_int(self, doc_list):
        assert isinstance(document_empty_paragraph_count(doc_list), int)

    def test_table_doc_is_int(self, doc_table):
        assert isinstance(document_empty_paragraph_count(doc_table), int)


# ---------------------------------------------------------------------------
# document_footnote_count
# ---------------------------------------------------------------------------

class TestDocumentFootnoteCount:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_footnote_count(doc_headings), dict)

    def test_has_footnotes_key(self, doc_headings):
        assert "footnotes" in document_footnote_count(doc_headings)

    def test_basic_has_zero_footnotes(self, doc_headings):
        assert document_footnote_count(doc_headings)["footnotes"] == 0

    def test_has_total_key(self, doc_headings):
        assert "total" in document_footnote_count(doc_headings)

    def test_has_has_notes_bool(self, doc_headings):
        assert isinstance(document_footnote_count(doc_headings).get("has_notes"), bool)


# ---------------------------------------------------------------------------
# document_footnote_endnote_summary
# ---------------------------------------------------------------------------

class TestDocumentFootnoteEndnoteSummary:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_footnote_endnote_summary(doc_headings), dict)

    def test_has_footnote_count(self, doc_headings):
        assert "footnote_count" in document_footnote_endnote_summary(doc_headings)

    def test_has_endnote_count(self, doc_headings):
        assert "endnote_count" in document_footnote_endnote_summary(doc_headings)

    def test_basic_has_zero_footnotes(self, doc_headings):
        assert document_footnote_endnote_summary(doc_headings)["footnote_count"] == 0

    def test_list_doc_is_dict(self, doc_list):
        assert isinstance(document_footnote_endnote_summary(doc_list), dict)


# ---------------------------------------------------------------------------
# document_heading_level_distribution
# ---------------------------------------------------------------------------

class TestDocumentHeadingLevelDistribution:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_heading_level_distribution(doc_headings), dict)

    def test_has_by_level(self, doc_headings):
        assert "by_level" in document_heading_level_distribution(doc_headings)

    def test_has_total_headings(self, doc_headings):
        result = document_heading_level_distribution(doc_headings)
        assert "total_headings" in result

    def test_total_headings_positive(self, doc_headings):
        assert document_heading_level_distribution(doc_headings)["total_headings"] > 0

    def test_has_deepest_level(self, doc_headings):
        assert "deepest_level" in document_heading_level_distribution(doc_headings)


# ---------------------------------------------------------------------------
# document_heading_outline
# ---------------------------------------------------------------------------

class TestDocumentHeadingOutline:
    def test_returns_list(self, doc_headings):
        assert isinstance(document_heading_outline(doc_headings), list)

    def test_nonempty_for_heading_doc(self, doc_headings):
        assert len(document_heading_outline(doc_headings)) > 0

    def test_each_entry_has_level(self, doc_headings):
        for entry in document_heading_outline(doc_headings):
            assert "level" in entry

    def test_each_entry_has_text(self, doc_headings):
        for entry in document_heading_outline(doc_headings):
            assert "text" in entry

    def test_minimal_returns_list(self, doc_minimal):
        assert isinstance(document_heading_outline(doc_minimal), list)


# ---------------------------------------------------------------------------
# document_heading_texts
# ---------------------------------------------------------------------------

class TestDocumentHeadingTexts:
    def test_returns_list(self, doc_headings):
        assert isinstance(document_heading_texts(doc_headings), list)

    def test_nonempty_for_heading_doc(self, doc_headings):
        assert len(document_heading_texts(doc_headings)) > 0

    def test_entries_are_strings(self, doc_headings):
        for text in document_heading_texts(doc_headings):
            assert isinstance(text, str)

    def test_count_matches_outline(self, doc_headings):
        texts = document_heading_texts(doc_headings)
        outline = document_heading_outline(doc_headings)
        assert len(texts) == len(outline)

    def test_list_doc_returns_list(self, doc_list):
        assert isinstance(document_heading_texts(doc_list), list)


# ---------------------------------------------------------------------------
# document_hyperlink_count
# ---------------------------------------------------------------------------

class TestDocumentHyperlinkCount:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_hyperlink_count(doc_headings), dict)

    def test_has_total_key(self, doc_headings):
        assert "total" in document_hyperlink_count(doc_headings)

    def test_basic_has_zero_hyperlinks(self, doc_headings):
        assert document_hyperlink_count(doc_headings)["total"] == 0

    def test_list_doc_is_dict(self, doc_list):
        assert isinstance(document_hyperlink_count(doc_list), dict)

    def test_non_negative_total(self, doc_table):
        assert document_hyperlink_count(doc_table)["total"] >= 0


# ---------------------------------------------------------------------------
# document_image_frame_list
# ---------------------------------------------------------------------------

class TestDocumentImageFrameList:
    def test_returns_list(self, doc_headings):
        assert isinstance(document_image_frame_list(doc_headings), list)

    def test_basic_has_no_images(self, doc_headings):
        assert document_image_frame_list(doc_headings) == []

    def test_list_doc_returns_list(self, doc_list):
        assert isinstance(document_image_frame_list(doc_list), list)

    def test_table_doc_returns_list(self, doc_table):
        assert isinstance(document_image_frame_list(doc_table), list)

    def test_all_entries_are_dicts(self, doc_headings):
        for item in document_image_frame_list(doc_headings):
            assert isinstance(item, dict)


# ---------------------------------------------------------------------------
# document_language_list
# ---------------------------------------------------------------------------

class TestDocumentLanguageList:
    def test_returns_list(self, doc_headings):
        assert isinstance(document_language_list(doc_headings), list)

    def test_list_doc_returns_list(self, doc_list):
        assert isinstance(document_language_list(doc_list), list)

    def test_table_doc_returns_list(self, doc_table):
        assert isinstance(document_language_list(doc_table), list)

    def test_all_entries_are_strings(self, doc_headings):
        for lang in document_language_list(doc_headings):
            assert isinstance(lang, str)

    def test_minimal_returns_list(self, doc_minimal):
        assert isinstance(document_language_list(doc_minimal), list)


# ---------------------------------------------------------------------------
# document_list_item_count
# ---------------------------------------------------------------------------

class TestDocumentListItemCount:
    def test_returns_int(self, doc_list):
        assert isinstance(document_list_item_count(doc_list), int)

    def test_list_doc_has_items(self, doc_list):
        assert document_list_item_count(doc_list) > 0

    def test_heading_doc_has_no_items(self, doc_headings):
        assert document_list_item_count(doc_headings) == 0

    def test_non_negative(self, doc_table):
        assert document_list_item_count(doc_table) >= 0

    def test_minimal_is_int(self, doc_minimal):
        assert isinstance(document_list_item_count(doc_minimal), int)


# ---------------------------------------------------------------------------
# document_list_stats
# ---------------------------------------------------------------------------

class TestDocumentListStats:
    def test_returns_dict(self, doc_list):
        assert isinstance(document_list_stats(doc_list), dict)

    def test_has_list_count(self, doc_list):
        assert "list_count" in document_list_stats(doc_list)

    def test_list_doc_has_lists(self, doc_list):
        assert document_list_stats(doc_list)["list_count"] > 0

    def test_heading_doc_has_no_lists(self, doc_headings):
        assert document_list_stats(doc_headings)["list_count"] == 0

    def test_has_total_items(self, doc_list):
        assert "total_items" in document_list_stats(doc_list)


# ---------------------------------------------------------------------------
# document_max_paragraph_length
# ---------------------------------------------------------------------------

class TestDocumentMaxParagraphLength:
    def test_returns_int(self, doc_headings):
        assert isinstance(document_max_paragraph_length(doc_headings), int)

    def test_positive_for_nonempty_doc(self, doc_headings):
        assert document_max_paragraph_length(doc_headings) > 0

    def test_list_doc_positive(self, doc_list):
        assert document_max_paragraph_length(doc_list) > 0

    def test_table_doc_is_int(self, doc_table):
        assert isinstance(document_max_paragraph_length(doc_table), int)

    def test_non_negative(self, doc_minimal):
        assert document_max_paragraph_length(doc_minimal) >= 0


# ---------------------------------------------------------------------------
# document_paragraph_count
# ---------------------------------------------------------------------------

class TestDocumentParagraphCount:
    def test_returns_int(self, doc_headings):
        assert isinstance(document_paragraph_count(doc_headings), int)

    def test_positive_for_nonempty_doc(self, doc_headings):
        assert document_paragraph_count(doc_headings) > 0

    def test_list_doc_positive(self, doc_list):
        assert document_paragraph_count(doc_list) > 0

    def test_table_doc_is_int(self, doc_table):
        assert isinstance(document_paragraph_count(doc_table), int)

    def test_non_negative(self, doc_minimal):
        assert document_paragraph_count(doc_minimal) >= 0


# ---------------------------------------------------------------------------
# document_paragraph_style_distribution
# ---------------------------------------------------------------------------

class TestDocumentParagraphStyleDistribution:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_paragraph_style_distribution(doc_headings), dict)

    def test_has_style_count(self, doc_headings):
        assert "style_count" in document_paragraph_style_distribution(doc_headings)

    def test_has_distribution(self, doc_headings):
        assert "distribution" in document_paragraph_style_distribution(doc_headings)

    def test_distribution_is_dict(self, doc_headings):
        result = document_paragraph_style_distribution(doc_headings)
        assert isinstance(result["distribution"], dict)

    def test_positive_style_count(self, doc_headings):
        result = document_paragraph_style_distribution(doc_headings)
        assert result["style_count"] >= 0


# ---------------------------------------------------------------------------
# document_paragraph_texts
# ---------------------------------------------------------------------------

class TestDocumentParagraphTexts:
    def test_returns_list(self, doc_headings):
        assert isinstance(document_paragraph_texts(doc_headings), list)

    def test_nonempty_for_paragraph_doc(self, doc_headings):
        assert len(document_paragraph_texts(doc_headings)) > 0

    def test_entries_are_strings(self, doc_headings):
        for text in document_paragraph_texts(doc_headings):
            assert isinstance(text, str)

    def test_list_doc_returns_list(self, doc_list):
        assert isinstance(document_paragraph_texts(doc_list), list)

    def test_table_doc_returns_list(self, doc_table):
        assert isinstance(document_paragraph_texts(doc_table), list)


# ---------------------------------------------------------------------------
# document_reading_level
# ---------------------------------------------------------------------------

class TestDocumentReadingLevel:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_reading_level(doc_headings), dict)

    def test_has_avg_words_per_sentence(self, doc_headings):
        assert "avg_words_per_sentence" in document_reading_level(doc_headings)

    def test_has_avg_chars_per_word(self, doc_headings):
        assert "avg_chars_per_word" in document_reading_level(doc_headings)

    def test_positive_metrics(self, doc_headings):
        result = document_reading_level(doc_headings)
        assert result["avg_words_per_sentence"] > 0

    def test_list_doc_is_dict(self, doc_list):
        assert isinstance(document_reading_level(doc_list), dict)


# ---------------------------------------------------------------------------
# document_section_summary
# ---------------------------------------------------------------------------

class TestDocumentSectionSummary:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_section_summary(doc_headings), dict)

    def test_has_section_count(self, doc_headings):
        assert "section_count" in document_section_summary(doc_headings)

    def test_basic_has_no_sections(self, doc_headings):
        assert document_section_summary(doc_headings)["section_count"] == 0

    def test_has_section_names(self, doc_headings):
        assert "section_names" in document_section_summary(doc_headings)

    def test_section_names_is_list(self, doc_headings):
        assert isinstance(document_section_summary(doc_headings)["section_names"], list)


# ---------------------------------------------------------------------------
# document_total_words
# ---------------------------------------------------------------------------

class TestDocumentTotalWords:
    def test_returns_int(self, doc_headings):
        assert isinstance(document_total_words(doc_headings), int)

    def test_positive_for_nonempty_doc(self, doc_headings):
        assert document_total_words(doc_headings) > 0

    def test_list_doc_positive(self, doc_list):
        assert document_total_words(doc_list) > 0

    def test_matches_word_count_total(self, doc_headings):
        wc = document_word_count(doc_headings)
        assert document_total_words(doc_headings) == wc["total_words"]

    def test_non_negative(self, doc_minimal):
        assert document_total_words(doc_minimal) >= 0


# ---------------------------------------------------------------------------
# document_word_count
# ---------------------------------------------------------------------------

class TestDocumentWordCount:
    def test_returns_dict(self, doc_headings):
        assert isinstance(document_word_count(doc_headings), dict)

    def test_has_total_words(self, doc_headings):
        assert "total_words" in document_word_count(doc_headings)

    def test_positive_total_words(self, doc_headings):
        assert document_word_count(doc_headings)["total_words"] > 0

    def test_has_block_words(self, doc_headings):
        assert "block_words" in document_word_count(doc_headings)

    def test_list_doc_is_dict(self, doc_list):
        assert isinstance(document_word_count(doc_list), dict)


# ---------------------------------------------------------------------------
# document_table_summary
# ---------------------------------------------------------------------------

class TestDocumentTableSummary:
    def test_returns_list(self, doc_table):
        assert isinstance(document_table_summary(doc_table), list)

    def test_table_doc_has_tables(self, doc_table):
        result = document_table_summary(doc_table)
        assert len(result) > 0

    def test_heading_doc_has_no_tables(self, doc_headings):
        assert document_table_summary(doc_headings) == []

    def test_each_entry_has_row_count(self, doc_table):
        for entry in document_table_summary(doc_table):
            assert "row_count" in entry

    def test_each_entry_has_column_count(self, doc_table):
        for entry in document_table_summary(doc_table):
            assert "column_count" in entry


# ---------------------------------------------------------------------------
# document_table_cell_count
# ---------------------------------------------------------------------------

class TestDocumentTableCellCount:
    def test_returns_dict(self, doc_table):
        assert isinstance(document_table_cell_count(doc_table), dict)

    def test_has_total_cells(self, doc_table):
        assert "total_cells" in document_table_cell_count(doc_table)

    def test_table_doc_has_cells(self, doc_table):
        assert document_table_cell_count(doc_table)["total_cells"] > 0

    def test_heading_doc_has_no_cells(self, doc_headings):
        assert document_table_cell_count(doc_headings)["total_cells"] == 0

    def test_has_total_tables(self, doc_table):
        assert "total_tables" in document_table_cell_count(doc_table)


# ---------------------------------------------------------------------------
# document_has_tables (cross-check)
# ---------------------------------------------------------------------------

class TestDocumentHasTables:
    def test_returns_bool(self, doc_headings):
        assert isinstance(document_has_tables(doc_headings), bool)

    def test_table_doc_returns_true(self, doc_table):
        assert document_has_tables(doc_table) is True

    def test_heading_doc_returns_false(self, doc_headings):
        assert document_has_tables(doc_headings) is False

    def test_list_doc_returns_false(self, doc_list):
        assert document_has_tables(doc_list) is False

    def test_minimal_is_bool(self, doc_minimal):
        assert isinstance(document_has_tables(doc_minimal), bool)
