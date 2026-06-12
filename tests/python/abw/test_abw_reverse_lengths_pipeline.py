"""
test_abw_reverse_lengths_pipeline.py -- ABW reverse_paragraphs + paragraph_lengths pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-87
Tests reverse_paragraphs returns model, first/last swapped, paragraph_lengths returns list,
lengths count matches paragraphs, lengths are ints.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    reverse_paragraphs,
    paragraph_lengths,
)

_PARAGRAPHS = ["Short.", "A medium length paragraph here.", "The longest paragraph of all is this one in the list."]


def test_reverse_paragraphs_returns_model(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = reverse_paragraphs(model)
    assert isinstance(result, dict)
    assert "paragraphs" in result


def test_reverse_paragraphs_first_last_swapped(tmp_path):
    model = create_abw(_PARAGRAPHS)
    orig_first = model["paragraphs"][0]
    orig_last = model["paragraphs"][-1]
    result = reverse_paragraphs(model)
    assert result["paragraphs"][0] == orig_last
    assert result["paragraphs"][-1] == orig_first


def test_paragraph_lengths_returns_list(tmp_path):
    model = create_abw(_PARAGRAPHS)
    lengths = paragraph_lengths(model)
    assert isinstance(lengths, list)


def test_paragraph_lengths_count_matches(tmp_path):
    model = create_abw(_PARAGRAPHS)
    lengths = paragraph_lengths(model)
    assert len(lengths) == 3


def test_paragraph_lengths_are_ints(tmp_path):
    model = create_abw(_PARAGRAPHS)
    lengths = paragraph_lengths(model)
    for length in lengths:
        assert isinstance(length, int)
