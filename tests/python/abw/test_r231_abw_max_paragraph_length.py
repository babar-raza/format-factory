"""Tests for abw_max_paragraph_length and abw_unique_word_count.

Product deepening: ABW analytics — TC-H3-002-ABW / PDC-ABW-MAX-PARAGRAPH-LENGTH-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_max_paragraph_length,
    abw_unique_word_count,
    create_abw,
    write_abw,
)

SAMPLES = _REPO / "samples" / "by-format" / "abw"


def _make_abw(tmp_path, name, paragraphs):
    model = create_abw(paragraphs)
    path = tmp_path / f"{name}.abw"
    write_abw(model, str(path))
    return path


class TestAbwMaxParagraphLength:
    def test_single_paragraph(self, tmp_path):
        f = _make_abw(tmp_path, "single", ["hello world"])
        assert abw_max_paragraph_length(f) == 11

    def test_multiple_paragraphs(self, tmp_path):
        f = _make_abw(tmp_path, "multi", ["short", "a longer paragraph here", "mid"])
        assert abw_max_paragraph_length(f) == 23

    def test_empty_document(self, tmp_path):
        f = _make_abw(tmp_path, "empty", [])
        assert abw_max_paragraph_length(f) == 0

    def test_empty_paragraphs(self, tmp_path):
        f = _make_abw(tmp_path, "blanks", ["", "", "abc"])
        assert abw_max_paragraph_length(f) == 3

    def test_returns_int(self, tmp_path):
        f = _make_abw(tmp_path, "type", ["test"])
        result = abw_max_paragraph_length(f)
        assert isinstance(result, int)

    def test_from_sample(self):
        path = SAMPLES / "two-paragraphs.abw"
        if path.exists():
            result = abw_max_paragraph_length(path)
            assert isinstance(result, int)
            assert result > 0


class TestAbwUniqueWordCount:
    def test_no_duplicates(self, tmp_path):
        f = _make_abw(tmp_path, "unique", ["hello world foo"])
        assert abw_unique_word_count(f) == 3

    def test_with_duplicates(self, tmp_path):
        f = _make_abw(tmp_path, "dups", ["hello hello world"])
        assert abw_unique_word_count(f) == 2

    def test_case_insensitive(self, tmp_path):
        f = _make_abw(tmp_path, "case", ["Hello HELLO hello"])
        assert abw_unique_word_count(f) == 1

    def test_empty_document(self, tmp_path):
        f = _make_abw(tmp_path, "empty2", [])
        assert abw_unique_word_count(f) == 0

    def test_across_paragraphs(self, tmp_path):
        f = _make_abw(tmp_path, "across", ["hello world", "world foo"])
        assert abw_unique_word_count(f) == 3

    def test_returns_int(self, tmp_path):
        f = _make_abw(tmp_path, "type2", ["test"])
        assert isinstance(abw_unique_word_count(f), int)

    def test_from_sample(self):
        path = SAMPLES / "two-paragraphs.abw"
        if path.exists():
            result = abw_unique_word_count(path)
            assert isinstance(result, int)
            assert result >= 0
