"""Gap closure tests for ABW — covering 22 open gaps.

Gaps cover: load, create_abw, write_abw, probe_abw, export_to_txt,
    export_to_html, export_to_json, get_metadata, get_paragraph_count,
    get_paragraph, extract_text, search_text, get_word_count,
    abw_word_count, abw_sentence_count, abw_longest_word,
    abw_total_char_count, abw_empty_paragraph_count,
    abw_nonempty_paragraph_count, abw_average_word_length,
    AbwError, AbwParseError
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    AbwError,
    AbwParseError,
    abw_average_word_length,
    abw_empty_paragraph_count,
    abw_longest_word,
    abw_nonempty_paragraph_count,
    abw_sentence_count,
    abw_total_char_count,
    abw_word_count,
    create_abw,
    export_to_html,
    export_to_json,
    export_to_txt,
    extract_text,
    get_metadata,
    get_paragraph,
    get_paragraph_count,
    get_word_count,
    load,
    probe_abw,
    search_text,
    write_abw,
)

SAMPLES = _REPO / "samples" / "by-format" / "abw"
MINIMAL = SAMPLES / "minimal-document.abw"
TWO_PARA = SAMPLES / "two-paragraphs.abw"


@pytest.fixture
def doc():
    return load(str(TWO_PARA))


@pytest.fixture
def abw_path():
    return str(TWO_PARA)


class TestErrorClasses:
    def test_abw_error_is_exception(self):
        assert issubclass(AbwError, Exception)

    def test_abw_parse_error_subclass(self):
        assert issubclass(AbwParseError, (AbwError, Exception))

    def test_message_preserved(self):
        err = AbwError("bad abw")
        assert "bad abw" in str(err)


class TestLoad:
    def test_returns_dict(self):
        doc = load(str(MINIMAL))
        assert isinstance(doc, dict)


class TestCreateAbw:
    def test_creates_doc(self):
        doc = create_abw(["Hello world"])
        assert doc is not None


class TestWriteAbw:
    def test_creates_file(self, doc, tmp_path):
        out = tmp_path / "out.abw"
        write_abw(doc, str(out))
        assert out.exists()
        assert out.stat().st_size > 0


class TestProbeAbw:
    def test_valid_file(self):
        result = probe_abw(str(MINIMAL))
        assert result is not None


class TestExportToTxt:
    def test_returns_string(self, abw_path):
        result = export_to_txt(abw_path)
        assert isinstance(result, str)


class TestExportToHtml:
    def test_returns_string(self, abw_path):
        result = export_to_html(abw_path)
        assert isinstance(result, str)
        assert "<" in result


class TestExportToJson:
    def test_returns_string(self, abw_path):
        result = export_to_json(abw_path)
        assert isinstance(result, str)


class TestGetMetadata:
    def test_returns_dict(self, abw_path):
        meta = get_metadata(abw_path)
        assert isinstance(meta, dict)


class TestGetParagraphCount:
    def test_returns_int(self, abw_path):
        count = get_paragraph_count(abw_path)
        assert isinstance(count, int)
        assert count >= 1


class TestGetParagraph:
    def test_returns_result(self, doc):
        para = get_paragraph(doc, 0)
        assert para is not None


class TestExtractText:
    def test_returns_result(self, abw_path):
        text = extract_text(abw_path)
        assert isinstance(text, (str, list))
        if isinstance(text, list):
            assert len(text) > 0
        else:
            assert len(text) > 0


class TestSearchText:
    def test_returns_list(self, doc):
        results = search_text(doc, "the")
        assert isinstance(results, list)


class TestGetWordCount:
    def test_returns_int(self, doc):
        count = get_word_count(doc)
        assert isinstance(count, int)
        assert count >= 0


class TestAbwWordCount:
    def test_returns_int(self, abw_path):
        count = abw_word_count(abw_path)
        assert isinstance(count, int)
        assert count >= 0


class TestAbwSentenceCount:
    def test_returns_int(self, doc):
        count = abw_sentence_count(doc)
        assert isinstance(count, int)
        assert count >= 0


class TestAbwLongestWord:
    def test_returns_string(self, doc):
        word = abw_longest_word(doc)
        assert isinstance(word, str)


class TestAbwTotalCharCount:
    def test_returns_int(self, abw_path):
        count = abw_total_char_count(abw_path)
        assert isinstance(count, int)
        assert count >= 0


class TestAbwEmptyParagraphCount:
    def test_returns_int(self, abw_path):
        count = abw_empty_paragraph_count(abw_path)
        assert isinstance(count, int)
        assert count >= 0


class TestAbwNonemptyParagraphCount:
    def test_returns_int(self, abw_path):
        count = abw_nonempty_paragraph_count(abw_path)
        assert isinstance(count, int)
        assert count >= 0


class TestAbwAverageWordLength:
    def test_returns_number(self, abw_path):
        avg = abw_average_word_length(abw_path)
        assert isinstance(avg, (int, float))
        assert avg >= 0
