"""
test_abw_search_replace_batch.py -- ABW search and replace batch pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-45
Tests search_paragraph finds query, search_replace_paragraph replaces,
search_text finds indices, get_paragraph_at index, has_paragraph after replace.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    search_paragraph,
    search_replace_paragraph,
    search_text,
    get_paragraph_at,
    has_paragraph,
)

_MODEL = create_abw([
    "The quick brown fox",
    "jumps over the lazy dog",
    "Python is great for automation",
    "The fox ran quickly away",
])


def test_search_paragraph_finds_match():
    results = search_paragraph(_MODEL, "fox")
    assert len(results) > 0


def test_search_replace_paragraph_replaces():
    model = create_abw(["The quick brown fox", "A second paragraph"])
    model = search_replace_paragraph(model, "fox", "cat")
    # search_paragraph finds substring match
    results = search_paragraph(model, "cat")
    assert len(results) > 0


def test_search_text_returns_indices():
    indices = search_text(_MODEL, "fox")
    assert isinstance(indices, list)
    assert len(indices) >= 2  # appears in paragraphs 0 and 3


def test_get_paragraph_at_correct():
    para = get_paragraph_at(_MODEL, 2)
    assert "Python" in para


def test_has_paragraph_after_replace():
    model = create_abw(["Hello world", "Second line"])
    model = search_replace_paragraph(model, "world", "universe")
    # has_paragraph checks exact match; check the full paragraph text
    assert has_paragraph(model, "Hello universe")
    assert not has_paragraph(model, "Hello world")
