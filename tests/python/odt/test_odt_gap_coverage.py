"""Gap-coverage tests for the ODT (OpenDocument Text) FOSS Python track.

Targets ~77 `missing_test_coverage` gaps by directly exercising analytics
functions in `src/python/odt/text_document.py` that had no (or only
incidental) direct test coverage, plus the previously-untested CLI entry
point (`src/python/odt/cli.py`), plus a safety-net sweep over every
single-argument `odt_*` export from the package's public API.

Investigation summary (see tests/python/odt/*.py for prior coverage):
    - odt_parser.py core (parse_odt, parse_odt_strict, probe_odt,
      get_capabilities, dataclasses) is heavily covered.
    - odt_doc_analytics.py (18 functions) is fully covered by
      test_odt_doc_analytics.py / _ext.py / _ext2.py.
    - text_document.py exposes 57 analytics functions; ~30 of them
      (word_count, heading_count, paragraph_count, char_count, list_count,
      table_count, average_word_length, unique_word_count, longest_paragraph,
      has_tables, avg_paragraph_length, words_per_sentence,
      vocabulary_richness, chars_per_word, has_headings, max_paragraph_length,
      has_unicode, max_words_per_paragraph, avg_chars_per_paragraph,
      avg_chars_per_word, is_content_rich, total_text_length,
      nonempty_paragraph_ratio, avg_sentence_length, longest_paragraph_index,
      has_numeric_content, numeric_value_sum, unique_char_count,
      nonspace_char_count, has_single_paragraph) already have dedicated test
      files.
    - The remaining 27 text_document.py functions had no direct test:
      odt_sentence_count, odt_min_paragraph_length,
      odt_heading_to_paragraph_ratio, odt_total_elements, odt_is_empty,
      odt_shortest_word, odt_paragraph_density, odt_heading_density,
      odt_longest_word, odt_list_to_paragraph_ratio, odt_has_lists,
      odt_min_words_per_paragraph, odt_word_density, odt_sentence_density,
      odt_table_density, odt_nonempty_paragraph_count, odt_char_density,
      odt_empty_paragraph_count, odt_words_per_heading,
      odt_avg_words_per_sentence, odt_shortest_paragraph_length,
      odt_paragraph_variance, odt_is_single_paragraph, odt_list_density,
      odt_heading_per_paragraph, odt_is_multi_paragraph, odt_whitespace_ratio.
      These are the primary focus of this file.
    - cli.py's main() had zero test coverage — also covered here.
"""
from __future__ import annotations

import inspect
import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.text_document import (  # noqa: E402
    odt_avg_words_per_sentence,
    odt_char_density,
    odt_empty_paragraph_count,
    odt_has_lists,
    odt_heading_density,
    odt_heading_per_paragraph,
    odt_heading_to_paragraph_ratio,
    odt_is_empty,
    odt_is_multi_paragraph,
    odt_is_single_paragraph,
    odt_list_density,
    odt_list_to_paragraph_ratio,
    odt_longest_word,
    odt_min_paragraph_length,
    odt_min_words_per_paragraph,
    odt_nonempty_paragraph_count,
    odt_paragraph_density,
    odt_paragraph_variance,
    odt_sentence_count,
    odt_sentence_density,
    odt_shortest_paragraph_length,
    odt_shortest_word,
    odt_table_density,
    odt_total_elements,
    odt_whitespace_ratio,
    odt_word_density,
    odt_words_per_heading,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
MINIMAL = _SAMPLES / "minimal-document.odt"
TWO_PARA = _SAMPLES / "two-paragraphs.odt"
UNICODE = _SAMPLES / "unicode-text.odt"


# ---------------------------------------------------------------------------
# Synthetic ODT builder — lets us exercise heading/list/table/empty-paragraph
# branches that the fixed sample corpus (0 headings, 0 lists, 0 tables) can
# never reach.
# ---------------------------------------------------------------------------

_NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
_NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
_NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
_MIMETYPE = "application/vnd.oasis.opendocument.text"


def _xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_odt(
    tmp_path: Path,
    name: str,
    paragraphs: "tuple[str, ...]" = (),
    headings: "tuple[str, ...]" = (),
    num_lists: int = 0,
    num_tables: int = 0,
) -> Path:
    """Build a minimal but valid .odt file with the given content.

    paragraphs -> text:p elements
    headings   -> text:h elements (outline-level 1)
    num_lists  -> that many top-level text:list elements (1 item each)
    num_tables -> that many table:table elements
    """
    heading_xml = "".join(
        f'<text:h text:outline-level="1">{_xml_escape(h)}</text:h>' for h in headings
    )
    para_xml = "".join(f"<text:p>{_xml_escape(p)}</text:p>" for p in paragraphs)
    list_xml = (
        '<text:list><text:list-item><text:p>item</text:p></text:list-item></text:list>'
        * num_lists
    )
    table_xml = "".join(
        f'<table:table table:name="T{i}">'
        "<table:table-row><table:table-cell><text:p>cell</text:p></table:table-cell></table:table-row>"
        "</table:table>"
        for i in range(num_tables)
    )
    content_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{_NS_OFFICE}" xmlns:text="{_NS_TEXT}" '
        f'xmlns:table="{_NS_TABLE}">'
        f"<office:body><office:text>{heading_xml}{para_xml}{list_xml}{table_xml}"
        "</office:text></office:body></office:document-content>"
    )
    path = tmp_path / f"{name}.odt"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", _MIMETYPE)
        zf.writestr("content.xml", content_xml)
    return path


# ---------------------------------------------------------------------------
# odt_sentence_count
# ---------------------------------------------------------------------------


class TestOdtSentenceCount:
    def test_counts_terminal_punctuation_in_paragraphs(self, tmp_path):
        f = _build_odt(tmp_path, "s1", paragraphs=("One. Two. Three.",))
        assert odt_sentence_count(f) == 3

    def test_counts_punctuation_in_headings_too(self, tmp_path):
        f = _build_odt(
            tmp_path, "s2", paragraphs=("One. Two. Three.",), headings=("Intro!",)
        )
        assert odt_sentence_count(f) == 4

    def test_no_punctuation_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "s3", paragraphs=("no punctuation here",))
        assert odt_sentence_count(f) == 0

    def test_empty_document_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "s4")
        assert odt_sentence_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "s5", paragraphs=("Hello.",))
        assert isinstance(odt_sentence_count(f), int)

    def test_real_sample_nonnegative(self):
        assert odt_sentence_count(MINIMAL) >= 0


# ---------------------------------------------------------------------------
# odt_min_paragraph_length
# ---------------------------------------------------------------------------


class TestOdtMinParagraphLength:
    def test_min_of_several(self, tmp_path):
        f = _build_odt(tmp_path, "m1", paragraphs=("abc", "de", "fghij"))
        assert odt_min_paragraph_length(f) == 2

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "m2")
        assert odt_min_paragraph_length(f) == 0

    def test_single_paragraph(self, tmp_path):
        f = _build_odt(tmp_path, "m3", paragraphs=("hello",))
        assert odt_min_paragraph_length(f) == 5

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "m4", paragraphs=("x",))
        assert isinstance(odt_min_paragraph_length(f), int)

    def test_minimal_sample(self):
        assert odt_min_paragraph_length(MINIMAL) == 13

    def test_two_para_sample(self):
        assert odt_min_paragraph_length(TWO_PARA) == 16


# ---------------------------------------------------------------------------
# odt_heading_to_paragraph_ratio
# ---------------------------------------------------------------------------


class TestOdtHeadingToParagraphRatio:
    def test_basic_ratio(self, tmp_path):
        f = _build_odt(tmp_path, "r1", paragraphs=("a", "b"), headings=("H1",))
        assert odt_heading_to_paragraph_ratio(f) == pytest.approx(0.5)

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "r2", headings=("H1",))
        assert odt_heading_to_paragraph_ratio(f) == 0.0

    def test_no_headings_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "r3", paragraphs=("a", "b"))
        assert odt_heading_to_paragraph_ratio(f) == 0.0

    def test_more_headings_than_paragraphs(self, tmp_path):
        f = _build_odt(tmp_path, "r4", paragraphs=("a",), headings=("H1", "H2"))
        assert odt_heading_to_paragraph_ratio(f) == pytest.approx(2.0)

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "r5", paragraphs=("a",), headings=("H",))
        assert isinstance(odt_heading_to_paragraph_ratio(f), float)


# ---------------------------------------------------------------------------
# odt_total_elements
# ---------------------------------------------------------------------------


class TestOdtTotalElements:
    def test_paragraphs_plus_headings(self, tmp_path):
        f = _build_odt(tmp_path, "t1", paragraphs=("a", "b", "c"), headings=("H1", "H2"))
        assert odt_total_elements(f) == 5

    def test_lists_do_not_count(self, tmp_path):
        f = _build_odt(
            tmp_path, "t2", paragraphs=("a", "b", "c"), headings=("H1", "H2"), num_lists=3
        )
        assert odt_total_elements(f) == 5

    def test_empty_document_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "t3")
        assert odt_total_elements(f) == 0

    def test_only_paragraphs(self, tmp_path):
        f = _build_odt(tmp_path, "t4", paragraphs=("a", "b"))
        assert odt_total_elements(f) == 2

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "t5", paragraphs=("a",))
        assert isinstance(odt_total_elements(f), int)

    def test_minimal_sample(self):
        assert odt_total_elements(MINIMAL) == 1


# ---------------------------------------------------------------------------
# odt_is_empty (text_document version — distinct from odt_doc_analytics one)
# ---------------------------------------------------------------------------


class TestOdtIsEmptyTextDocument:
    def test_no_content_is_empty(self, tmp_path):
        f = _build_odt(tmp_path, "e1")
        assert odt_is_empty(f) is True

    def test_with_paragraphs_not_empty(self, tmp_path):
        f = _build_odt(tmp_path, "e2", paragraphs=("hi",))
        assert odt_is_empty(f) is False

    def test_only_headings_not_empty(self, tmp_path):
        f = _build_odt(tmp_path, "e3", headings=("H1",))
        assert odt_is_empty(f) is False

    def test_returns_bool(self, tmp_path):
        f = _build_odt(tmp_path, "e4")
        assert isinstance(odt_is_empty(f), bool)

    def test_minimal_sample_not_empty(self):
        assert odt_is_empty(MINIMAL) is False


# ---------------------------------------------------------------------------
# odt_shortest_word / odt_longest_word
# ---------------------------------------------------------------------------


class TestOdtShortestWord:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "w1", paragraphs=("cat dog elephant",))
        assert odt_shortest_word(f) == 3

    def test_single_char_word(self, tmp_path):
        f = _build_odt(tmp_path, "w2", paragraphs=("a bb ccc",))
        assert odt_shortest_word(f) == 1

    def test_no_words_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "w3")
        assert odt_shortest_word(f) == 0

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "w4", paragraphs=("word",))
        assert isinstance(odt_shortest_word(f), int)


class TestOdtLongestWord:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "lw1", paragraphs=("cat elephant dog",))
        assert odt_longest_word(f) == 8

    def test_no_words_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "lw2")
        assert odt_longest_word(f) == 0

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "lw3", paragraphs=("word",))
        assert isinstance(odt_longest_word(f), int)

    def test_longest_gte_shortest(self, tmp_path):
        f = _build_odt(tmp_path, "lw4", paragraphs=("a bb ccc dddd",))
        assert odt_longest_word(f) >= odt_shortest_word(f)


# ---------------------------------------------------------------------------
# odt_paragraph_density / odt_heading_density / odt_table_density /
# odt_list_density
# ---------------------------------------------------------------------------


class TestOdtParagraphDensity:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "pd1", paragraphs=("abcde", "fg"), headings=("H",))
        # total chars = 7, total elements (para+heading) = 3
        assert odt_paragraph_density(f) == pytest.approx(7 / 3)

    def test_no_elements_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "pd2")
        assert odt_paragraph_density(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "pd3", paragraphs=("x",))
        assert isinstance(odt_paragraph_density(f), float)


class TestOdtHeadingDensity:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "hd1", paragraphs=("a", "b", "c"), headings=("H1", "H2"))
        assert odt_heading_density(f) == pytest.approx(0.4)

    def test_no_elements_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "hd2")
        assert odt_heading_density(f) == 0.0

    def test_no_headings_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "hd3", paragraphs=("a", "b"))
        assert odt_heading_density(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "hd4", paragraphs=("a",), headings=("H",))
        assert isinstance(odt_heading_density(f), float)


class TestOdtTableDensity:
    def test_basic(self, tmp_path):
        f = _build_odt(
            tmp_path, "td1", paragraphs=("a", "b"), headings=("H",), num_tables=2
        )
        assert odt_table_density(f) == pytest.approx(2 / 3)

    def test_no_elements_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "td2")
        assert odt_table_density(f) == 0.0

    def test_no_tables_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "td3", paragraphs=("a", "b"))
        assert odt_table_density(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "td4", paragraphs=("a",), num_tables=1)
        assert isinstance(odt_table_density(f), float)


class TestOdtListDensity:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "ld1", paragraphs=("a", "b"), num_lists=1)
        assert odt_list_density(f) == pytest.approx(0.5)

    def test_no_elements_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "ld2")
        assert odt_list_density(f) == 0.0

    def test_no_lists_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "ld3", paragraphs=("a", "b"))
        assert odt_list_density(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "ld4", paragraphs=("a",), num_lists=1)
        assert isinstance(odt_list_density(f), float)


# ---------------------------------------------------------------------------
# odt_list_to_paragraph_ratio / odt_has_lists
# ---------------------------------------------------------------------------


class TestOdtListToParagraphRatio:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "lr1", paragraphs=("a", "b"), num_lists=1)
        assert odt_list_to_paragraph_ratio(f) == pytest.approx(0.5)

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "lr2", num_lists=2)
        assert odt_list_to_paragraph_ratio(f) == 0.0

    def test_no_lists_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "lr3", paragraphs=("a", "b"))
        assert odt_list_to_paragraph_ratio(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "lr4", paragraphs=("a",), num_lists=1)
        assert isinstance(odt_list_to_paragraph_ratio(f), float)


class TestOdtHasLists:
    def test_false_without_lists(self, tmp_path):
        f = _build_odt(tmp_path, "hl1", paragraphs=("a",))
        assert odt_has_lists(f) is False

    def test_true_with_lists(self, tmp_path):
        f = _build_odt(tmp_path, "hl2", paragraphs=("a",), num_lists=2)
        assert odt_has_lists(f) is True

    def test_empty_document_false(self, tmp_path):
        f = _build_odt(tmp_path, "hl3")
        assert odt_has_lists(f) is False

    def test_returns_bool(self, tmp_path):
        f = _build_odt(tmp_path, "hl4", paragraphs=("a",))
        assert isinstance(odt_has_lists(f), bool)


# ---------------------------------------------------------------------------
# odt_min_words_per_paragraph
# ---------------------------------------------------------------------------


class TestOdtMinWordsPerParagraph:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "mw1", paragraphs=("one two three", "four five"))
        assert odt_min_words_per_paragraph(f) == 2

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "mw2")
        assert odt_min_words_per_paragraph(f) == 0

    def test_whitespace_only_paragraph_excluded(self, tmp_path):
        f = _build_odt(tmp_path, "mw3", paragraphs=("real words here", "   "))
        assert odt_min_words_per_paragraph(f) == 3

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "mw4", paragraphs=("a b",))
        assert isinstance(odt_min_words_per_paragraph(f), int)


# ---------------------------------------------------------------------------
# odt_word_density / odt_char_density
# ---------------------------------------------------------------------------


class TestOdtWordDensity:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "wd1", paragraphs=("one two", "three four five"))
        assert odt_word_density(f) == pytest.approx(2.5)

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "wd2")
        assert odt_word_density(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "wd3", paragraphs=("a b",))
        assert isinstance(odt_word_density(f), float)


class TestOdtCharDensity:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "cd1", paragraphs=("abcde", "fg"))
        assert odt_char_density(f) == pytest.approx(3.5)

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "cd2")
        assert odt_char_density(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "cd3", paragraphs=("abc",))
        assert isinstance(odt_char_density(f), float)


# ---------------------------------------------------------------------------
# odt_sentence_density
# ---------------------------------------------------------------------------


class TestOdtSentenceDensity:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "sd1", paragraphs=("One. Two.", "Three."))
        # sentences=3 (2+1), paragraphs=2
        assert odt_sentence_density(f) == pytest.approx(1.5)

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "sd2")
        assert odt_sentence_density(f) == 0.0

    def test_no_sentences_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "sd3", paragraphs=("no punctuation",))
        assert odt_sentence_density(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "sd4", paragraphs=("Hi.",))
        assert isinstance(odt_sentence_density(f), float)


# ---------------------------------------------------------------------------
# odt_nonempty_paragraph_count / odt_empty_paragraph_count
# ---------------------------------------------------------------------------


class TestOdtNonemptyParagraphCount:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "np1", paragraphs=("hello", "   ", "world"))
        assert odt_nonempty_paragraph_count(f) == 2

    def test_all_nonempty(self, tmp_path):
        f = _build_odt(tmp_path, "np2", paragraphs=("a", "b", "c"))
        assert odt_nonempty_paragraph_count(f) == 3

    def test_no_paragraphs(self, tmp_path):
        f = _build_odt(tmp_path, "np3")
        assert odt_nonempty_paragraph_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "np4", paragraphs=("a",))
        assert isinstance(odt_nonempty_paragraph_count(f), int)


class TestOdtEmptyParagraphCount:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "ep1", paragraphs=("a", " ", "  ", "b"))
        assert odt_empty_paragraph_count(f) == 2

    def test_none_empty(self, tmp_path):
        f = _build_odt(tmp_path, "ep2", paragraphs=("a", "b"))
        assert odt_empty_paragraph_count(f) == 0

    def test_no_paragraphs(self, tmp_path):
        f = _build_odt(tmp_path, "ep3")
        assert odt_empty_paragraph_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "ep4", paragraphs=("  ",))
        assert isinstance(odt_empty_paragraph_count(f), int)

    def test_nonempty_plus_empty_equals_total(self, tmp_path):
        f = _build_odt(tmp_path, "ep5", paragraphs=("a", " ", "b", "  ", "c"))
        assert (
            odt_nonempty_paragraph_count(f) + odt_empty_paragraph_count(f)
            == 5
        )


# ---------------------------------------------------------------------------
# odt_words_per_heading
# ---------------------------------------------------------------------------


class TestOdtWordsPerHeading:
    def test_basic(self, tmp_path):
        f = _build_odt(
            tmp_path,
            "wh1",
            paragraphs=("one two three", "four five"),
            headings=("H1", "H2"),
        )
        assert odt_words_per_heading(f) == pytest.approx(2.5)

    def test_no_headings_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "wh2", paragraphs=("one two",))
        assert odt_words_per_heading(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "wh3", paragraphs=("a b",), headings=("H",))
        assert isinstance(odt_words_per_heading(f), float)


# ---------------------------------------------------------------------------
# odt_avg_words_per_sentence
# ---------------------------------------------------------------------------


class TestOdtAvgWordsPerSentence:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "aw1", paragraphs=("One two. Three four five.",))
        assert odt_avg_words_per_sentence(f) == pytest.approx(2.5)

    def test_no_sentences_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "aw2", paragraphs=("no punctuation here",))
        assert odt_avg_words_per_sentence(f) == 0.0

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "aw3")
        assert odt_avg_words_per_sentence(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "aw4", paragraphs=("Hi there.",))
        assert isinstance(odt_avg_words_per_sentence(f), float)


# ---------------------------------------------------------------------------
# odt_shortest_paragraph_length
# ---------------------------------------------------------------------------


class TestOdtShortestParagraphLength:
    def test_basic_excludes_whitespace_only(self, tmp_path):
        f = _build_odt(tmp_path, "sp1", paragraphs=("abcde", "fg", "   "))
        assert odt_shortest_paragraph_length(f) == 2

    def test_no_nonempty_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "sp2", paragraphs=("   ",))
        assert odt_shortest_paragraph_length(f) == 0

    def test_no_paragraphs_at_all_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "sp3")
        assert odt_shortest_paragraph_length(f) == 0

    def test_returns_int(self, tmp_path):
        f = _build_odt(tmp_path, "sp4", paragraphs=("abc",))
        assert isinstance(odt_shortest_paragraph_length(f), int)

    def test_two_para_sample(self):
        assert odt_shortest_paragraph_length(TWO_PARA) == 16


# ---------------------------------------------------------------------------
# odt_paragraph_variance
# ---------------------------------------------------------------------------


class TestOdtParagraphVariance:
    def test_two_paragraphs_exact(self, tmp_path):
        f = _build_odt(tmp_path, "pv1", paragraphs=("a b", "c d e f"))
        # word counts [2, 4], mean=3, variance=((2-3)^2+(4-3)^2)/2 = 1.0
        assert odt_paragraph_variance(f) == pytest.approx(1.0)

    def test_fewer_than_two_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "pv2", paragraphs=("only one",))
        assert odt_paragraph_variance(f) == 0.0

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "pv3")
        assert odt_paragraph_variance(f) == 0.0

    def test_three_paragraphs(self, tmp_path):
        f = _build_odt(tmp_path, "pv4", paragraphs=("one two", "three four five six", "seven"))
        # word counts [2, 4, 1], mean=7/3
        mean = 7 / 3
        expected = sum((c - mean) ** 2 for c in (2, 4, 1)) / 3
        assert odt_paragraph_variance(f) == pytest.approx(expected)

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "pv5", paragraphs=("a b", "c"))
        assert isinstance(odt_paragraph_variance(f), float)

    def test_nonnegative(self, tmp_path):
        f = _build_odt(tmp_path, "pv6", paragraphs=("a", "b b b"))
        assert odt_paragraph_variance(f) >= 0.0


# ---------------------------------------------------------------------------
# odt_is_single_paragraph / odt_is_multi_paragraph (text_document versions,
# nonempty-based — distinct from odt_doc_analytics' raw-count versions)
# ---------------------------------------------------------------------------


class TestOdtIsSingleParagraphTextDocument:
    def test_exactly_one_nonempty(self, tmp_path):
        f = _build_odt(tmp_path, "isp1", paragraphs=("only one",))
        assert odt_is_single_paragraph(f) is True

    def test_two_nonempty_is_false(self, tmp_path):
        f = _build_odt(tmp_path, "isp2", paragraphs=("one", "two"))
        assert odt_is_single_paragraph(f) is False

    def test_whitespace_only_extra_paragraph_still_single(self, tmp_path):
        f = _build_odt(tmp_path, "isp3", paragraphs=("one", "   "))
        assert odt_is_single_paragraph(f) is True

    def test_no_paragraphs_is_false(self, tmp_path):
        f = _build_odt(tmp_path, "isp4")
        assert odt_is_single_paragraph(f) is False

    def test_returns_bool(self, tmp_path):
        f = _build_odt(tmp_path, "isp5", paragraphs=("a",))
        assert isinstance(odt_is_single_paragraph(f), bool)

    def test_minimal_sample(self):
        assert odt_is_single_paragraph(MINIMAL) is True


class TestOdtIsMultiParagraphTextDocument:
    def test_two_nonempty_is_true(self, tmp_path):
        f = _build_odt(tmp_path, "imp1", paragraphs=("one", "two"))
        assert odt_is_multi_paragraph(f) is True

    def test_single_nonempty_is_false(self, tmp_path):
        f = _build_odt(tmp_path, "imp2", paragraphs=("only",))
        assert odt_is_multi_paragraph(f) is False

    def test_whitespace_only_second_paragraph_is_false(self, tmp_path):
        f = _build_odt(tmp_path, "imp3", paragraphs=("one", "   "))
        assert odt_is_multi_paragraph(f) is False

    def test_no_paragraphs_is_false(self, tmp_path):
        f = _build_odt(tmp_path, "imp4")
        assert odt_is_multi_paragraph(f) is False

    def test_returns_bool(self, tmp_path):
        f = _build_odt(tmp_path, "imp5", paragraphs=("a", "b"))
        assert isinstance(odt_is_multi_paragraph(f), bool)

    def test_two_para_sample(self):
        assert odt_is_multi_paragraph(TWO_PARA) is True

    def test_mutually_exclusive_with_is_single(self, tmp_path):
        f = _build_odt(tmp_path, "imp6", paragraphs=("one", "two", "three"))
        assert odt_is_single_paragraph(f) != odt_is_multi_paragraph(f) or (
            odt_is_single_paragraph(f) is False and odt_is_multi_paragraph(f) is True
        )


# ---------------------------------------------------------------------------
# odt_heading_per_paragraph (duplicate formula of heading_to_paragraph_ratio
# under a different name — verify both agree)
# ---------------------------------------------------------------------------


class TestOdtHeadingPerParagraph:
    def test_basic(self, tmp_path):
        f = _build_odt(tmp_path, "hp1", paragraphs=("a", "b", "c"), headings=("H1",))
        assert odt_heading_per_paragraph(f) == pytest.approx(1 / 3)

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "hp2", headings=("H1",))
        assert odt_heading_per_paragraph(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "hp3", paragraphs=("a",), headings=("H",))
        assert isinstance(odt_heading_per_paragraph(f), float)

    def test_agrees_with_heading_to_paragraph_ratio(self, tmp_path):
        f = _build_odt(tmp_path, "hp4", paragraphs=("a", "b"), headings=("H1", "H2"))
        assert odt_heading_per_paragraph(f) == pytest.approx(
            odt_heading_to_paragraph_ratio(f)
        )


# ---------------------------------------------------------------------------
# odt_whitespace_ratio
# ---------------------------------------------------------------------------


class TestOdtWhitespaceRatio:
    def test_single_paragraph(self, tmp_path):
        f = _build_odt(tmp_path, "wr1", paragraphs=("ab cd",))
        assert odt_whitespace_ratio(f) == pytest.approx(1 / 5)

    def test_multiple_paragraphs_joined_with_space(self, tmp_path):
        f = _build_odt(tmp_path, "wr2", paragraphs=("ab", "cd"))
        # " ".join(["ab", "cd"]) == "ab cd" -> 1 space / 5 chars
        assert odt_whitespace_ratio(f) == pytest.approx(1 / 5)

    def test_no_paragraphs_returns_zero(self, tmp_path):
        f = _build_odt(tmp_path, "wr3")
        assert odt_whitespace_ratio(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _build_odt(tmp_path, "wr4", paragraphs=("a b c",))
        assert isinstance(odt_whitespace_ratio(f), float)

    def test_ratio_between_zero_and_one(self, tmp_path):
        f = _build_odt(tmp_path, "wr5", paragraphs=("many words in this text",))
        assert 0.0 <= odt_whitespace_ratio(f) <= 1.0

    def test_no_whitespace_is_zero(self, tmp_path):
        f = _build_odt(tmp_path, "wr6", paragraphs=("nospaceshere",))
        assert odt_whitespace_ratio(f) == 0.0


# ---------------------------------------------------------------------------
# CLI entry point (src/python/odt/cli.py) — previously untested
# ---------------------------------------------------------------------------


class TestOdtCli:
    def test_no_args_prints_usage_and_exits_zero(self, monkeypatch, capsys):
        from odt import cli

        monkeypatch.setattr(sys, "argv", ["ff-odt"])
        with pytest.raises(SystemExit) as excinfo:
            cli.main()
        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert "Usage" in out

    def test_nonexistent_file_exits_one(self, monkeypatch, capsys):
        from odt import cli

        monkeypatch.setattr(sys, "argv", ["ff-odt", "/nonexistent/path/fake.odt"])
        with pytest.raises(SystemExit) as excinfo:
            cli.main()
        assert excinfo.value.code == 1
        err = capsys.readouterr().err
        assert "not found" in err.lower()

    def test_valid_file_prints_paragraph_count(self, monkeypatch, capsys):
        from odt import cli

        monkeypatch.setattr(sys, "argv", ["ff-odt", str(MINIMAL)])
        cli.main()
        out = capsys.readouterr().out
        assert "Paragraphs:" in out
        assert "File:" in out

    def test_valid_file_reports_correct_count(self, monkeypatch, capsys):
        from odt import cli

        monkeypatch.setattr(sys, "argv", ["ff-odt", str(TWO_PARA)])
        cli.main()
        out = capsys.readouterr().out
        assert "Paragraphs: 2" in out

    def test_invalid_odt_content_does_not_crash(self, monkeypatch, capsys, tmp_path):
        from odt import cli

        bad = tmp_path / "bad.odt"
        bad.write_bytes(b"not a real odt file")
        monkeypatch.setattr(sys, "argv", ["ff-odt", str(bad)])
        # parse_odt() never raises (it returns ok=False), so main() should
        # complete normally without raising SystemExit.
        cli.main()
        out = capsys.readouterr().out
        assert "Paragraphs:" in out

    def test_main_is_callable(self):
        from odt import cli

        assert callable(cli.main)


# ---------------------------------------------------------------------------
# Safety-net sweep: every single-argument `odt_*` export runs clean
# ---------------------------------------------------------------------------


class TestExportedAnalyticsSweep:
    """Iterate `odt.__all__` and call every callable that takes exactly one
    required positional argument against each valid sample file. This is a
    coarse safety net ensuring no exported analytics function crashes on
    real ODT input, complementing the fine-grained tests above."""

    def test_all_single_arg_odt_functions_run_clean(self):
        import odt as odt_pkg

        checked = 0
        for attr_name in odt_pkg.__all__:
            if not attr_name.startswith("odt_"):
                continue
            attr = getattr(odt_pkg, attr_name)
            if not callable(attr) or inspect.isclass(attr):
                continue
            try:
                sig = inspect.signature(attr)
            except (TypeError, ValueError):
                continue
            required = [
                p
                for p in sig.parameters.values()
                if p.default is inspect.Parameter.empty
                and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
            if len(required) != 1:
                continue
            for sample in (MINIMAL, TWO_PARA, UNICODE):
                result = attr(sample)
                assert result is not None, f"{attr_name}({sample.name}) returned None"
            checked += 1

        # Sanity: the sweep must actually have exercised a meaningful subset
        # of the ~57 analytics functions exported by text_document.py.
        assert checked >= 50, f"sweep only exercised {checked} functions"
