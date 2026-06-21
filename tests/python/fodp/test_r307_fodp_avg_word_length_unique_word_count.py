"""Tests for fodp_avg_word_length and fodp_unique_word_count (Sprint 97, R307)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_avg_word_length, fodp_unique_word_count

FODP = _REPO / "samples" / "by-format" / "fodp"


def test_avg_word_length_minimal():
    assert abs(fodp_avg_word_length(FODP / "minimal-presentation.fodp") - 5.0) < 0.01


def test_avg_word_length_title_only():
    assert abs(fodp_avg_word_length(FODP / "title-only.fodp") - 0.0) < 0.01


def test_avg_word_length_two_slides():
    assert abs(fodp_avg_word_length(FODP / "two-slides-basic.fodp") - 8.0) < 0.01


def test_avg_word_length_returns_float():
    assert isinstance(fodp_avg_word_length(FODP / "minimal-presentation.fodp"), float)


def test_avg_word_length_nonnegative():
    assert fodp_avg_word_length(FODP / "title-only.fodp") >= 0.0


def test_unique_word_count_minimal():
    assert fodp_unique_word_count(FODP / "minimal-presentation.fodp") == 1


def test_unique_word_count_title_only():
    assert fodp_unique_word_count(FODP / "title-only.fodp") == 0


def test_unique_word_count_two_slides():
    assert fodp_unique_word_count(FODP / "two-slides-basic.fodp") == 5


def test_unique_word_count_returns_int():
    assert isinstance(fodp_unique_word_count(FODP / "minimal-presentation.fodp"), int)


def test_unique_word_count_nonnegative():
    assert fodp_unique_word_count(FODP / "title-only.fodp") >= 0
