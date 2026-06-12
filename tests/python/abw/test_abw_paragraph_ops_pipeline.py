"""
test_abw_paragraph_ops_pipeline.py -- ABW paragraph operations pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-60
Tests append_paragraph increases count, join_paragraphs string, replace_in_paragraphs,
split_paragraphs list, truncate_paragraphs count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    append_paragraph,
    join_paragraphs,
    replace_in_paragraphs,
    split_paragraphs,
    truncate_paragraphs,
)

_MODEL = create_abw(["Hello world", "Second line", "Third line"])


def test_append_paragraph_increases_count():
    model = append_paragraph(_MODEL, "New paragraph")
    assert model["paragraph_count"] == 4


def test_join_paragraphs_string():
    result = join_paragraphs(_MODEL, " | ")
    assert isinstance(result, str)
    assert "Hello world" in result


def test_replace_in_paragraphs():
    model = replace_in_paragraphs(_MODEL, "world", "universe")
    assert "Hello universe" in model["paragraphs"]


def test_split_paragraphs_list():
    chunks = split_paragraphs(_MODEL, 2)
    assert isinstance(chunks, list)
    assert len(chunks) >= 2


def test_truncate_paragraphs_count():
    model = truncate_paragraphs(_MODEL, 2)
    assert model["paragraph_count"] == 2
    assert len(model["paragraphs"]) == 2
