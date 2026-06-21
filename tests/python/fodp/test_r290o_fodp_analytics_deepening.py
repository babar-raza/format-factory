"""Tests for FODP analytics deepening (R290O): longest_slide_text, avg_word_count_per_slide, shortest_slide_text."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_longest_slide_text, fodp_avg_word_count_per_slide, fodp_shortest_slide_text

SAMPLES = _REPO / "samples" / "by-format" / "fodp"


def test_longest_slide_text_returns_int():
    result = fodp_longest_slide_text(SAMPLES / "two-slides-basic.fodp")
    assert isinstance(result, int)
    assert result >= 0


def test_longest_slide_text_minimal():
    result = fodp_longest_slide_text(SAMPLES / "minimal-presentation.fodp")
    assert isinstance(result, int)


def test_avg_word_count_per_slide_returns_float():
    result = fodp_avg_word_count_per_slide(SAMPLES / "two-slides-basic.fodp")
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_word_count_per_slide_title():
    result = fodp_avg_word_count_per_slide(SAMPLES / "title-only.fodp")
    assert isinstance(result, float)


def test_shortest_slide_text_returns_int():
    result = fodp_shortest_slide_text(SAMPLES / "two-slides-basic.fodp")
    assert isinstance(result, int)
    assert result >= 0


def test_shortest_slide_text_minimal():
    result = fodp_shortest_slide_text(SAMPLES / "minimal-presentation.fodp")
    assert isinstance(result, int)
