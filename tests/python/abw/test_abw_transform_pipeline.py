"""
test_abw_transform_pipeline.py -- ABW word_wrap + split_paragraphs transform pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-33
Tests word_wrap (count unchanged), split_paragraphs, truncate_paragraphs,
reverse_paragraphs, join_paragraphs.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    word_wrap,
    split_paragraphs,
    truncate_paragraphs,
    reverse_paragraphs,
    join_paragraphs,
)

_MODEL = create_abw(["Hello World Today", "Goodbye World", "Third paragraph"])


def test_word_wrap_paragraph_count_unchanged():
    m2 = word_wrap(_MODEL, width=80)
    assert m2["paragraph_count"] == 3


def test_split_paragraphs_chunks():
    # split into chunks of 2 paragraphs
    chunks = split_paragraphs(_MODEL, chunk_size=2)
    assert len(chunks) == 2  # [chunk1(2 paras), chunk2(1 para)]


def test_truncate_paragraphs():
    m2 = truncate_paragraphs(_MODEL, n=2)
    assert m2["paragraph_count"] == 2


def test_reverse_paragraphs_order():
    m2 = reverse_paragraphs(_MODEL)
    assert m2["paragraphs"][0] == "Third paragraph"
    assert m2["paragraphs"][-1] == "Hello World Today"


def test_join_paragraphs():
    joined = join_paragraphs(_MODEL, sep=" | ")
    assert "Hello World Today" in joined
    assert " | " in joined
