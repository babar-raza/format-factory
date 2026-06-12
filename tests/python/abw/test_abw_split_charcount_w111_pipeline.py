"""
test_abw_split_charcount_w111_pipeline.py -- ABW split_paragraphs + get_char_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-111
Tests split_paragraphs returns list, chunk_size=2 gives 2 chunks, get_char_count returns int,
char_count correct, char_count first chunk less than total.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    split_paragraphs,
    get_char_count,
)

_PARAGRAPHS = [
    "Hello World",
    "Quick brown fox",
    "One two three",
    "Test paragraph",
]


def _make_model():
    return create_abw(_PARAGRAPHS)


def test_split_paragraphs_returns_list():
    model = _make_model()
    result = split_paragraphs(model, 2)
    assert isinstance(result, list)


def test_split_paragraphs_chunk_size():
    model = _make_model()
    result = split_paragraphs(model, 2)
    assert len(result) == 2


def test_get_char_count_returns_int():
    model = _make_model()
    assert isinstance(get_char_count(model), int)


def test_get_char_count_correct():
    model = _make_model()
    expected = sum(len(p) for p in _PARAGRAPHS)
    assert get_char_count(model) == expected


def test_char_count_first_chunk_less_than_total():
    model = _make_model()
    chunks = split_paragraphs(model, 2)
    total = get_char_count(model)
    first_chunk_count = get_char_count(chunks[0])
    assert first_chunk_count < total
