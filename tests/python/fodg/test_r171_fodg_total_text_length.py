"""Tests for fodg_codec.total_text_length() — Sprint 4 Lane D (LFI-6-D).

Verifies total character count of all text across all pages in a FODG model.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import add_page, create_fodg, total_text_length


def test_empty_model_has_zero_length():
    model = create_fodg([])
    assert total_text_length(model) == 0


def test_single_text_length():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["Hello"]})
    assert total_text_length(model) == len("Hello")


def test_multiple_texts_summed():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["abc", "de"]})
    assert total_text_length(model) == 5  # 3 + 2


def test_multiple_pages_summed():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["Hello"]})
    model = add_page(model, {"name": "P2", "texts": ["World!"]})
    assert total_text_length(model) == len("Hello") + len("World!")


def test_empty_text_strings_counted_as_zero():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["", "abc"]})
    assert total_text_length(model) == 3


def test_returns_int():
    model = create_fodg([])
    result = total_text_length(model)
    assert isinstance(result, int)


def test_unicode_text_length():
    model = create_fodg([])
    text = "caf\u00e9"  # 4 chars
    model = add_page(model, {"name": "P1", "texts": [text]})
    assert total_text_length(model) == 4
