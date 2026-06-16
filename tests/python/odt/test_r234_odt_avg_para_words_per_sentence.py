"""Tests for odt_avg_paragraph_length and odt_words_per_sentence (Sprint 24)."""
import sys
from pathlib import Path
import zipfile
import io

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import odt_avg_paragraph_length, odt_words_per_sentence


def _make_odt(tmp_path, name, paragraphs):
    content_xml = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
  <office:body>
    <office:text>
""" + "".join(f"      <text:p>{p}</text:p>\n" for p in paragraphs) + """    </office:text>
  </office:body>
</office:document-content>"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        zf.writestr("content.xml", content_xml.encode("utf-8"))
    p = tmp_path / f"{name}.odt"
    p.write_bytes(buf.getvalue())
    return str(p)


class TestOdtAvgParagraphLength:
    def test_return_type(self, tmp_path):
        p = _make_odt(tmp_path, "rt", ["Hello world"])
        result = odt_avg_paragraph_length(p)
        assert isinstance(result, float)

    def test_single_paragraph_exact(self, tmp_path):
        # "hello world" = 11 chars, 1 paragraph -> avg = 11.0
        p = _make_odt(tmp_path, "sp", ["hello world"])
        assert odt_avg_paragraph_length(p) == 11.0

    def test_empty_returns_zero(self, tmp_path):
        p = _make_odt(tmp_path, "ez", [])
        assert odt_avg_paragraph_length(p) == 0.0

    def test_two_equal_paragraphs(self, tmp_path):
        # "one two three" (13) + "four five six" (13) = 26/2 = 13.0
        p = _make_odt(tmp_path, "tp", ["one two three", "four five six"])
        assert odt_avg_paragraph_length(p) == 13.0

    def test_nonnegative(self, tmp_path):
        p = _make_odt(tmp_path, "nn", ["text"])
        assert odt_avg_paragraph_length(p) >= 0.0


class TestOdtWordsPerSentence:
    def test_return_type(self, tmp_path):
        p = _make_odt(tmp_path, "rt2", ["Hello world. Goodbye."])
        result = odt_words_per_sentence(p)
        assert isinstance(result, float)

    def test_two_sentences_exact(self, tmp_path):
        # "Hello world. Goodbye." -> 3 words, 2 sentences -> 3/2 = 1.5
        p = _make_odt(tmp_path, "ts", ["Hello world. Goodbye."])
        assert odt_words_per_sentence(p) == 1.5

    def test_empty_returns_zero(self, tmp_path):
        p = _make_odt(tmp_path, "ez2", [])
        assert odt_words_per_sentence(p) == 0.0

    def test_nonnegative(self, tmp_path):
        p = _make_odt(tmp_path, "nn2", ["A sentence here."])
        assert odt_words_per_sentence(p) >= 0.0

    def test_result_is_float(self, tmp_path):
        p = _make_odt(tmp_path, "rf", ["One two three. Four five."])
        result = odt_words_per_sentence(p)
        assert isinstance(result, float)
