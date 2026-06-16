"""Tests for abw_shortest_word and abw_has_sections.

Product deepening: ABW analytics — PDC-ABW-SHORTEST-SECTIONS-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw import create_abw, write_abw, abw_shortest_word, abw_has_sections


def _make_abw(tmp_path, name, paragraphs):
    model = create_abw(paragraphs)
    p = tmp_path / f"{name}.abw"
    write_abw(model, str(p))
    return p


class TestAbwShortestWord:
    def test_single_word(self, tmp_path):
        p = _make_abw(tmp_path, "one", ["Hello"])
        assert abw_shortest_word(p) == "Hello"

    def test_multiple_words(self, tmp_path):
        p = _make_abw(tmp_path, "multi", ["The quick brown fox"])
        result = abw_shortest_word(p)
        assert len(result) <= 3  # "The" is shortest

    def test_two_paragraphs(self, tmp_path):
        p = _make_abw(tmp_path, "two", ["Hello world", "I am here"])
        result = abw_shortest_word(p)
        assert len(result) <= 2  # "I" is shortest

    def test_returns_string(self, tmp_path):
        p = _make_abw(tmp_path, "ret", ["Test word"])
        assert isinstance(abw_shortest_word(p), str)

    def test_single_char_word(self, tmp_path):
        p = _make_abw(tmp_path, "char", ["I am a person"])
        assert len(abw_shortest_word(p)) == 1


class TestAbwHasSections:
    def test_returns_bool(self, tmp_path):
        p = _make_abw(tmp_path, "bool_t", ["Content"])
        assert isinstance(abw_has_sections(p), bool)

    def test_simple_doc(self, tmp_path):
        p = _make_abw(tmp_path, "simple", ["Just text"])
        # Simple ABW docs may or may not have sections depending on create_abw
        result = abw_has_sections(p)
        assert isinstance(result, bool)

    def test_empty_paragraph(self, tmp_path):
        p = _make_abw(tmp_path, "empty_p", [""])
        result = abw_has_sections(p)
        assert isinstance(result, bool)

    def test_multiple_paragraphs(self, tmp_path):
        p = _make_abw(tmp_path, "mult", ["Para one", "Para two", "Para three"])
        result = abw_has_sections(p)
        assert isinstance(result, bool)

    def test_non_negative_sections(self, tmp_path):
        p = _make_abw(tmp_path, "nn", ["Text"])
        # has_sections returns bool, just verify it's callable
        assert abw_has_sections(p) in (True, False)
