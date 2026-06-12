"""
Tests for ABW get_words() — returns tokenized words from a specific paragraph.

Sprint: FORMAT-FACTORY-SELF-HEALING-PRODUCT-DEEPENING-RNEXT
Taskcard: PD-Q-003
Queue item: pdrnext-q-003
Execution method: QUEUE_DISPATCHED_EXECUTION
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import get_words  # noqa: E402


def test_get_words_returns_list():
    model = {"paragraphs": ["hello world"]}
    result = get_words(model, 0)
    assert isinstance(result, list)


def test_get_words_basic_split():
    model = {"paragraphs": ["hello world foo"]}
    assert get_words(model, 0) == ["hello", "world", "foo"]


def test_get_words_single_word():
    model = {"paragraphs": ["hello"]}
    assert get_words(model, 0) == ["hello"]


def test_get_words_invalid_index_high():
    model = {"paragraphs": ["hello world"]}
    assert get_words(model, 5) == []


def test_get_words_invalid_index_negative():
    model = {"paragraphs": ["hello world"]}
    assert get_words(model, -1) == []


def test_get_words_empty_paragraph():
    model = {"paragraphs": [""]}
    assert get_words(model, 0) == []


def test_get_words_whitespace_only():
    model = {"paragraphs": ["   "]}
    assert get_words(model, 0) == []


def test_get_words_multi_paragraph():
    model = {"paragraphs": ["one two", "three four five"]}
    assert get_words(model, 1) == ["three", "four", "five"]


def test_get_words_non_dict_model():
    assert get_words([], 0) == []
    assert get_words("string", 0) == []


def test_get_words_empty_paragraphs():
    model = {"paragraphs": []}
    assert get_words(model, 0) == []


def test_get_words_preserves_word_content():
    model = {"paragraphs": ["The quick brown fox"]}
    words = get_words(model, 0)
    assert "quick" in words
    assert "brown" in words
    assert len(words) == 4


def test_get_words_importable_from_package():
    from abw import get_words as fn
    assert callable(fn)
