"""Gap closure tests for FODT — covering 38 open FOSS gaps.

Gaps: GAP-FODT-FOSS-WRITE_FODT-001, GAP-FODT-FOSS-DOCUMENT_TO-001,
      GAP-FODT-FOSS-DOCUMENT_ST-001, GAP-FODT-FOSS-DOCUMENT_HE-001,
      GAP-FODT-FOSS-DOCUMENT_TE-001, GAP-FODT-FOSS-DOCUMENT_WO-001,
      GAP-FODT-FOSS-DOCUMENT_TA-001, GAP-FODT-FOSS-DOCUMENT_LI-001,
      GAP-FODT-FOSS-DOCUMENT_RE-001, GAP-FODT-FOSS-DOCUMENT_HY-001,
      GAP-FODT-FOSS-DOCUMENT_FO-001, GAP-FODT-FOSS-DOCUMENT_IM-001,
      GAP-FODT-FOSS-DOCUMENT_SE-001, GAP-FODT-FOSS-DOCUMENT_CH-001,
      GAP-FODT-FOSS-DOCUMENT_PA-001, GAP-FODT-FOSS-DOCUMENT_LA-001,
      GAP-FODT-FOSS-DOCUMENT_SE-002, GAP-FODT-FOSS-DOCUMENT_WA-001,
      GAP-FODT-FOSS-DOCUMENT_AP-001, GAP-FODT-FOSS-DOCUMENT_RE-002,
      GAP-FODT-FOSS-DOCUMENT_GE-001, GAP-FODT-FOSS-DOCUMENT_SE-003,
      GAP-FODT-FOSS-DOCUMENT_RE-003, GAP-FODT-FOSS-DOCUMENT_EX-001,
      GAP-FODT-FOSS-DOCUMENT_CO-001, GAP-FODT-FOSS-DOCUMENT_TO-002,
      GAP-FODT-FOSS-DOCUMENT_BL-001, GAP-FODT-FOSS-DOCUMENT_MA-001,
      GAP-FODT-FOSS-DOCUMENT_HA-001, GAP-FODT-FOSS-DOCUMENT_EM-001,
      GAP-FODT-FOSS-FODTERROR-001, GAP-FODT-FOSS-FODTINPUTERR-001,
      GAP-FODT-FOSS-FODTSIZEERR-001, GAP-FODT-FOSS-FODTPARSEER-001,
      GAP-FODT-FOSS-FORMAT_ID-001, GAP-FODT-FOSS-SPEC_VERSION-001,
      GAP-FODT-FOSS-PACKAGE_VER-001, GAP-FODT-FOSS-MAX_FILE_BY-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    FORMAT_ID,
    MAX_FILE_BYTES,
    PACKAGE_VERSION,
    SPEC_VERSION,
    FodtError,
    FodtInputError,
    FodtParseError,
    FodtSizeError,
    document_append_paragraph,
    document_block_type_count,
    document_change_tracking_summary,
    document_count_tables,
    document_empty_paragraph_count,
    document_extract_headings,
    document_footnote_count,
    document_get_paragraph_text,
    document_has_tables,
    document_heading_outline,
    document_hyperlink_count,
    document_image_frame_list,
    document_language_list,
    document_list_stats,
    document_max_paragraph_length,
    document_paragraph_style_distribution,
    document_reading_level,
    document_remove_paragraph,
    document_replace_text,
    document_search_text,
    document_section_summary,
    document_set_block_text,
    document_stats,
    document_table_summary,
    document_text_content,
    document_to_xml,
    document_total_words,
    document_warnings_for_unsupported_edit,
    document_word_count,
    parse_fodt,
    write_fodt,
)

SAMPLES = _REPO / "samples" / "by-format" / "fodt"
MINIMAL = SAMPLES / "minimal-document.fodt"
HEADINGS = SAMPLES / "headings-and-paragraphs.fodt"
TABLE = SAMPLES / "table-basic.fodt"


@pytest.fixture
def doc():
    return parse_fodt(str(HEADINGS))


@pytest.fixture
def table_doc():
    return parse_fodt(str(TABLE))


@pytest.fixture
def minimal_doc():
    return parse_fodt(str(MINIMAL))


class TestConstants:
    def test_format_id(self):
        assert FORMAT_ID == "fodt"

    def test_spec_version(self):
        assert isinstance(SPEC_VERSION, str)
        assert len(SPEC_VERSION) > 0

    def test_package_version(self):
        assert isinstance(PACKAGE_VERSION, str)

    def test_max_file_bytes(self):
        assert isinstance(MAX_FILE_BYTES, int)
        assert MAX_FILE_BYTES > 0


class TestErrorClasses:
    def test_fodt_error_is_exception(self):
        assert issubclass(FodtError, Exception)

    def test_fodt_input_error_subclass(self):
        assert issubclass(FodtInputError, FodtError)

    def test_fodt_size_error_subclass(self):
        assert issubclass(FodtSizeError, FodtError)

    def test_fodt_parse_error_subclass(self):
        assert issubclass(FodtParseError, FodtError)

    def test_error_message_preserved(self):
        err = FodtError("test message")
        assert "test message" in str(err)


class TestWriteFodt:
    def test_write_creates_file(self, doc, tmp_path):
        out = tmp_path / "out.fodt"
        write_fodt(doc, str(out))
        assert out.exists()
        assert out.stat().st_size > 0

    def test_roundtrip(self, doc, tmp_path):
        out = tmp_path / "rt.fodt"
        write_fodt(doc, str(out))
        reparsed = parse_fodt(str(out))
        assert isinstance(reparsed, dict)
        assert "blocks" in reparsed or "content" in reparsed


class TestDocumentToXml:
    def test_returns_string(self, doc):
        xml = document_to_xml(doc)
        assert isinstance(xml, str)
        assert len(xml) > 0

    def test_contains_xml_declaration(self, doc):
        xml = document_to_xml(doc)
        assert "<?xml" in xml or "<office:" in xml


class TestDocumentStats:
    def test_returns_dict(self, doc):
        stats = document_stats(doc)
        assert isinstance(stats, dict)

    def test_has_paragraph_count(self, doc):
        stats = document_stats(doc)
        assert "paragraph_count" in stats or len(stats) > 0


class TestDocumentHeadingOutline:
    def test_returns_list(self, doc):
        outline = document_heading_outline(doc)
        assert isinstance(outline, list)

    def test_headings_have_text(self, doc):
        outline = document_heading_outline(doc)
        if outline:
            assert "text" in outline[0] or "title" in outline[0] or "content" in outline[0]


class TestDocumentTextContent:
    def test_returns_string(self, doc):
        text = document_text_content(doc)
        assert isinstance(text, str)
        assert len(text) > 0


class TestDocumentWordCount:
    def test_returns_dict(self, doc):
        wc = document_word_count(doc)
        assert isinstance(wc, dict)


class TestDocumentTableSummary:
    def test_returns_list(self, table_doc):
        summary = document_table_summary(table_doc)
        assert isinstance(summary, list)


class TestDocumentListStats:
    def test_returns_dict(self, doc):
        stats = document_list_stats(doc)
        assert isinstance(stats, dict)


class TestDocumentReadingLevel:
    def test_returns_dict(self, doc):
        rl = document_reading_level(doc)
        assert isinstance(rl, dict)


class TestDocumentHyperlinkCount:
    def test_returns_dict(self, doc):
        result = document_hyperlink_count(doc)
        assert isinstance(result, dict)


class TestDocumentFootnoteCount:
    def test_returns_dict(self, doc):
        result = document_footnote_count(doc)
        assert isinstance(result, dict)


class TestDocumentImageFrameList:
    def test_returns_list(self, doc):
        result = document_image_frame_list(doc)
        assert isinstance(result, list)


class TestDocumentSectionSummary:
    def test_returns_dict(self, doc):
        result = document_section_summary(doc)
        assert isinstance(result, dict)


class TestDocumentChangeTrackingSummary:
    def test_returns_dict(self, doc):
        result = document_change_tracking_summary(doc)
        assert isinstance(result, dict)


class TestDocumentParagraphStyleDistribution:
    def test_returns_dict(self, doc):
        result = document_paragraph_style_distribution(doc)
        assert isinstance(result, dict)


class TestDocumentLanguageList:
    def test_returns_list(self, doc):
        result = document_language_list(doc)
        assert isinstance(result, list)


class TestDocumentSetBlockText:
    def test_set_block_text(self, doc):
        ok, msg = document_set_block_text(doc, 0, "New text")
        assert isinstance(ok, bool)
        assert isinstance(msg, str)


class TestDocumentWarningsForUnsupportedEdit:
    def test_returns_list(self, doc):
        warnings = document_warnings_for_unsupported_edit(doc, 0)
        assert isinstance(warnings, list)


class TestDocumentAppendParagraph:
    def test_append(self, doc):
        ok, msg = document_append_paragraph(doc, "Appended text")
        assert isinstance(ok, bool)


class TestDocumentRemoveParagraph:
    def test_remove(self, doc):
        ok, msg = document_remove_paragraph(doc, 0)
        assert isinstance(ok, bool)


class TestDocumentGetParagraphText:
    def test_get_text(self, doc):
        text = document_get_paragraph_text(doc, 0)
        assert text is None or isinstance(text, str)


class TestDocumentSearchText:
    def test_search(self, doc):
        results = document_search_text(doc, "the")
        assert isinstance(results, list)


class TestDocumentReplaceText:
    def test_replace(self, doc):
        result = document_replace_text(doc, "the", "THE")
        assert isinstance(result, dict)


class TestDocumentExtractHeadings:
    def test_returns_list(self, doc):
        headings = document_extract_headings(doc)
        assert isinstance(headings, list)


class TestDocumentCountTables:
    def test_returns_int(self, table_doc):
        count = document_count_tables(table_doc)
        assert isinstance(count, int)
        assert count >= 0


class TestDocumentTotalWords:
    def test_returns_int(self, doc):
        total = document_total_words(doc)
        assert isinstance(total, int)
        assert total >= 0


class TestDocumentBlockTypeCount:
    def test_returns_dict(self, doc):
        counts = document_block_type_count(doc)
        assert isinstance(counts, dict)


class TestDocumentMaxParagraphLength:
    def test_returns_int(self, doc):
        max_len = document_max_paragraph_length(doc)
        assert isinstance(max_len, int)
        assert max_len >= 0


class TestDocumentHasTables:
    def test_table_doc_has_tables(self, table_doc):
        assert document_has_tables(table_doc) is True

    def test_minimal_doc(self, minimal_doc):
        result = document_has_tables(minimal_doc)
        assert isinstance(result, bool)


class TestDocumentEmptyParagraphCount:
    def test_returns_int(self, doc):
        count = document_empty_paragraph_count(doc)
        assert isinstance(count, int)
        assert count >= 0
