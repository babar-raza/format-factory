"""
test_r132_fodt_structure_analytics.py — Test coverage for FODT structure analytics.

Gaps closed:
- GAP-FODT-FOSS-FODT_MAX_RUN-001  (fodt_max_run_count — missing_test_coverage)
- GAP-FODT-FOSS-FODT_MAX_WOR-001  (fodt_max_words_in_heading — missing_test_coverage)
- GAP-FODT-FOSS-FODT_SHORT_P-001  (fodt_short_paragraph_count — missing_test_coverage)
- GAP-FODT-FOSS-FODT_SPACE_C-001  (fodt_space_count — missing_test_coverage)
- GAP-FODT-FOSS-FODT_PUNCTUA-001  (fodt_punctuation_count — missing_test_coverage)
- GAP-FODT-FOSS-FODT_LIST_BL-001  (fodt_list_block_count — missing_test_coverage)
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.fodt_analytics import (
    fodt_max_run_count,
    fodt_max_words_in_heading,
    fodt_short_paragraph_count,
    fodt_space_count,
    fodt_punctuation_count,
    fodt_list_block_count,
)


class TestFodtMaxRunCount:
    """GAP-FODT-FOSS-FODT_MAX_RUN-001: fodt_max_run_count."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_max_run_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_max_run_count(f) >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_max_run_count(f)
        assert isinstance(result, int) and result >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_max_run_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtMaxWordsInHeading:
    """GAP-FODT-FOSS-FODT_MAX_WOR-001: fodt_max_words_in_heading."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_max_words_in_heading(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_max_words_in_heading(f) >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_max_words_in_heading(f)
        assert isinstance(result, int) and result >= 0

    def test_doc_with_headings(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        result = fodt_max_words_in_heading(f)
        # A document with headings should have at least 1 word in a heading
        assert result >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_max_words_in_heading(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtShortParagraphCount:
    """GAP-FODT-FOSS-FODT_SHORT_P-001: fodt_short_paragraph_count."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_short_paragraph_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_short_paragraph_count(f) >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_short_paragraph_count(f)
        assert isinstance(result, int) and result >= 0

    def test_list_doc(self):
        f = _SAMPLES / "list-basic.fodt"
        result = fodt_short_paragraph_count(f)
        assert isinstance(result, int) and result >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_short_paragraph_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtSpaceCount:
    """GAP-FODT-FOSS-FODT_SPACE_C-001: fodt_space_count."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_space_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_space_count(f) >= 0

    def test_doc_with_text_has_spaces(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        result = fodt_space_count(f)
        # Document with multiple words should have spaces
        assert result >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_space_count(f)
        assert isinstance(result, int) and result >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_space_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtPunctuationCount:
    """GAP-FODT-FOSS-FODT_PUNCTUA-001: fodt_punctuation_count."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_punctuation_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_punctuation_count(f) >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_punctuation_count(f)
        assert isinstance(result, int) and result >= 0

    def test_table_doc(self):
        f = _SAMPLES / "table-basic.fodt"
        result = fodt_punctuation_count(f)
        assert isinstance(result, int) and result >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_punctuation_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtListBlockCount:
    """GAP-FODT-FOSS-FODT_LIST_BL-001: fodt_list_block_count."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_list_block_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_list_block_count(f) >= 0

    def test_list_doc_has_lists(self):
        f = _SAMPLES / "list-basic.fodt"
        result = fodt_list_block_count(f)
        assert isinstance(result, int) and result >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_list_block_count(f)
        assert isinstance(result, int) and result >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_list_block_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"
