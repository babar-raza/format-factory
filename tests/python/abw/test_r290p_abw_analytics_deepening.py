"""Tests for ABW analytics deepening (R290P): longest_paragraph_chars, shortest_paragraph_chars, avg_word_per_paragraph."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_longest_paragraph_chars, abw_shortest_paragraph_chars, abw_avg_word_per_paragraph

SAMPLES = _REPO / "samples" / "by-format" / "abw"


def test_longest_paragraph_chars_returns_int():
    result = abw_longest_paragraph_chars(SAMPLES / "two-paragraphs.abw")
    assert isinstance(result, int)
    assert result >= 0


def test_longest_paragraph_chars_minimal():
    result = abw_longest_paragraph_chars(SAMPLES / "minimal-document.abw")
    assert isinstance(result, int)


def test_shortest_paragraph_chars_returns_int():
    result = abw_shortest_paragraph_chars(SAMPLES / "two-paragraphs.abw")
    assert isinstance(result, int)
    assert result >= 0


def test_shortest_paragraph_chars_minimal():
    result = abw_shortest_paragraph_chars(SAMPLES / "minimal-document.abw")
    assert isinstance(result, int)


def test_avg_word_per_paragraph_returns_float():
    result = abw_avg_word_per_paragraph(SAMPLES / "two-paragraphs.abw")
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_word_per_paragraph_minimal():
    result = abw_avg_word_per_paragraph(SAMPLES / "minimal-document.abw")
    assert isinstance(result, float)
