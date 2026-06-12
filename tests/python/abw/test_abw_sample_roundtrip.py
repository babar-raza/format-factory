"""
test_abw_sample_roundtrip.py -- ABW sample file roundtrip and export content tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-14
Tests load from real ABW samples with exact content assertions,
export_to_plain_text, write/reload roundtrip.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "abw"

from abw.abw_codec import (
    load,
    extract_text,
    export_to_plain_text,
    write_abw,
    get_paragraph_count,
)


def test_two_paragraphs_load_count():
    result = load(str(_SAMPLES / "two-paragraphs.abw"))
    assert result["paragraph_count"] == 2


def test_two_paragraphs_exact_content():
    result = load(str(_SAMPLES / "two-paragraphs.abw"))
    assert result["paragraphs"][0] == "First paragraph."
    assert result["paragraphs"][1] == "Second paragraph."


def test_extract_text_returns_correct_list():
    texts = extract_text(str(_SAMPLES / "two-paragraphs.abw"))
    assert "First paragraph." in texts
    assert "Second paragraph." in texts


def test_export_to_plain_text_content():
    model = load(str(_SAMPLES / "two-paragraphs.abw"))
    plain = export_to_plain_text(model)
    assert "First paragraph." in plain
    assert "Second paragraph." in plain


def test_export_to_plain_text_separator():
    model = load(str(_SAMPLES / "two-paragraphs.abw"))
    plain = export_to_plain_text(model)
    # paragraphs separated by double newline
    assert "\n\n" in plain


def test_write_and_reload_preserves_paragraphs(tmp_path):
    original = load(str(_SAMPLES / "two-paragraphs.abw"))
    dest = tmp_path / "copy.abw"
    write_abw(original, str(dest))
    reloaded = load(str(dest))
    assert reloaded["paragraphs"] == original["paragraphs"]


def test_paragraph_count_function():
    count = get_paragraph_count(str(_SAMPLES / "two-paragraphs.abw"))
    assert count == 2
