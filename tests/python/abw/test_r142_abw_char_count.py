"""Tests for abw.abw_codec.get_char_count() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, get_char_count


def test_empty_model_zero():
    model = create_abw([])
    assert get_char_count(model) == 0


def test_single_paragraph():
    model = create_abw(["hello"])
    assert get_char_count(model) == 5


def test_multiple_paragraphs():
    model = create_abw(["abc", "de"])
    assert get_char_count(model) == 5


def test_counts_spaces():
    model = create_abw(["a b c"])
    assert get_char_count(model) == 5


def test_empty_paragraph_counts_zero():
    model = create_abw(["hello", "", "world"])
    assert get_char_count(model) == 10


def test_type_error():
    try:
        get_char_count("not a dict")
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_unicode_chars():
    model = create_abw(["héllo"])
    assert get_char_count(model) == 5


def test_large_count():
    model = create_abw(["x" * 1000, "y" * 2000])
    assert get_char_count(model) == 3000
