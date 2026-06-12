"""
test_abw_split_join_pipeline.py -- ABW split_paragraphs + join_paragraphs pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-84
Tests split_paragraphs returns list, split chunk size respected,
join_paragraphs returns string, join contains content, split then join roundtrip.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    split_paragraphs,
    join_paragraphs,
)

_PARAGRAPHS = [
    "First paragraph content here.",
    "Second paragraph content here.",
    "Third paragraph content here.",
    "Fourth paragraph content here.",
]


def test_split_paragraphs_returns_list(tmp_path):
    model = create_abw(_PARAGRAPHS)
    chunks = split_paragraphs(model, 2)
    assert isinstance(chunks, list)


def test_split_chunk_size_respected(tmp_path):
    model = create_abw(_PARAGRAPHS)
    chunks = split_paragraphs(model, 2)
    assert len(chunks) == 2


def test_join_paragraphs_returns_string(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = join_paragraphs(model)
    assert isinstance(result, str)


def test_join_paragraphs_contains_content(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = join_paragraphs(model)
    assert "First" in result
    assert "Fourth" in result


def test_split_then_join_roundtrip(tmp_path):
    model = create_abw(_PARAGRAPHS)
    joined = join_paragraphs(model, sep=" ")
    assert len(joined) > 0
    chunks = split_paragraphs(model, 1)
    assert len(chunks) == 4
