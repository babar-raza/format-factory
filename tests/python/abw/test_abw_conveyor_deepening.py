"""
test_abw_conveyor_deepening.py -- ABW product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-5
Tests export, search, merge, and utility functions for ABW.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "abw"

from abw.abw_codec import (
    load,
    create_abw,
    write_abw,
    export_to_txt,
    export_to_html,
    export_to_json,
    export_to_csv,
    get_metadata,
    search_paragraph,
    get_word_count,
    merge_abw,
    word_frequency,
    get_unique_words,
    append_paragraph,
    get_char_count,
    join_paragraphs,
)


def test_export_to_txt():
    txt = export_to_txt(_SAMPLES / "two-paragraphs.abw")
    assert isinstance(txt, str)
    assert len(txt) > 0


def test_export_to_html():
    html = export_to_html(_SAMPLES / "two-paragraphs.abw")
    assert isinstance(html, str)
    assert "<" in html


def test_export_to_json():
    json_str = export_to_json(_SAMPLES / "two-paragraphs.abw")
    assert isinstance(json_str, str)
    assert len(json_str) > 0


def test_export_to_csv():
    csv_str = export_to_csv(_SAMPLES / "two-paragraphs.abw")
    assert isinstance(csv_str, str)


def test_get_metadata():
    meta = get_metadata(_SAMPLES / "minimal-document.abw")
    assert isinstance(meta, dict)


def test_search_paragraph():
    model = load(_SAMPLES / "two-paragraphs.abw")
    results = search_paragraph(model, "")
    assert isinstance(results, list)


def test_get_word_count():
    model = load(_SAMPLES / "two-paragraphs.abw")
    count = get_word_count(model)
    assert isinstance(count, int)
    assert count >= 0


def test_word_frequency():
    model = load(_SAMPLES / "two-paragraphs.abw")
    freq = word_frequency(model)
    assert isinstance(freq, dict)


def test_get_unique_words():
    model = load(_SAMPLES / "two-paragraphs.abw")
    words = get_unique_words(model)
    assert isinstance(words, list)


def test_get_char_count():
    model = load(_SAMPLES / "two-paragraphs.abw")
    count = get_char_count(model)
    assert isinstance(count, int)
    assert count >= 0


def test_join_paragraphs():
    model = load(_SAMPLES / "two-paragraphs.abw")
    text = join_paragraphs(model)
    assert isinstance(text, str)


def test_create_write_roundtrip(tmp_path):
    model = create_abw(["Hello", "World"])
    out = tmp_path / "created.abw"
    write_abw(model, str(out))
    reloaded = load(out)
    assert reloaded["paragraph_count"] == 2


def test_append_paragraph():
    model = load(_SAMPLES / "minimal-document.abw")
    updated = append_paragraph(model, "New paragraph")
    assert updated["paragraph_count"] == model["paragraph_count"] + 1


def test_merge_abw():
    a = load(_SAMPLES / "minimal-document.abw")
    b = load(_SAMPLES / "two-paragraphs.abw")
    merged = merge_abw(a, b)
    assert merged["paragraph_count"] == a["paragraph_count"] + b["paragraph_count"]
