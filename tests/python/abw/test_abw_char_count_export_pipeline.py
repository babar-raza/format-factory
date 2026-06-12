"""
test_abw_char_count_export_pipeline.py -- ABW char count + export pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-63
Tests get_char_count int, export_to_markdown string, export_to_plain_text string,
export_to_markdown has content, char count > 0.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    get_char_count,
    export_to_markdown,
    export_to_plain_text,
)

_MODEL = create_abw([
    "Hello world",
    "Second paragraph",
    "Third paragraph here",
])


def test_get_char_count_int():
    count = get_char_count(_MODEL)
    assert isinstance(count, int)


def test_char_count_positive():
    count = get_char_count(_MODEL)
    assert count > 0


def test_export_to_markdown_string():
    result = export_to_markdown(_MODEL)
    assert isinstance(result, str)


def test_export_to_markdown_has_content():
    result = export_to_markdown(_MODEL)
    assert "Hello world" in result


def test_export_to_plain_text_string():
    result = export_to_plain_text(_MODEL)
    assert isinstance(result, str)
    assert "Second paragraph" in result
