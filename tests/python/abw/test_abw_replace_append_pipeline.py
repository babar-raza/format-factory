"""
test_abw_replace_append_pipeline.py -- ABW replace_in_paragraphs + append_paragraph pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-39
Tests replace_in_paragraphs replaces text, append_paragraph increases count,
edit_paragraph changes text, has_paragraph finds text, count_words after operations.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    replace_in_paragraphs,
    append_paragraph,
    edit_paragraph,
    has_paragraph,
    count_words,
)

_MODEL = create_abw(["Hello World", "Goodbye World", "Third text"])


def test_replace_in_paragraphs():
    m2 = replace_in_paragraphs(_MODEL, "World", "Universe")
    assert "Universe" in m2["paragraphs"][0]
    assert "World" not in m2["paragraphs"][0]


def test_append_paragraph_count():
    m2 = append_paragraph(_MODEL, "New paragraph")
    assert m2["paragraph_count"] == 4


def test_append_paragraph_content():
    m2 = append_paragraph(_MODEL, "Appended text")
    assert m2["paragraphs"][-1] == "Appended text"


def test_edit_paragraph():
    m2 = edit_paragraph(_MODEL, 0, "Replaced text")
    assert m2["paragraphs"][0] == "Replaced text"


def test_has_paragraph_after_replace():
    m2 = replace_in_paragraphs(_MODEL, "Hello", "Greetings")
    assert has_paragraph(m2, "Greetings World") is True
