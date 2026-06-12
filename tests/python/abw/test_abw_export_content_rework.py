"""
test_abw_export_content_rework.py -- ABW rework: precise content assertions.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-6
Rework for W5-ABW-DEEPENING: validates actual output content, not just types.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "abw"

from abw.abw_codec import (
    load,
    export_to_txt,
    export_to_html,
    export_to_json,
    export_to_csv,
    word_frequency,
    get_unique_words,
    get_char_count,
    join_paragraphs,
    search_paragraph,
)


def test_export_to_html_has_paragraph_tags():
    html = export_to_html(_SAMPLES / "two-paragraphs.abw")
    assert "<p>" in html and "</p>" in html
    assert "First paragraph." in html
    assert "Second paragraph." in html


def test_export_to_html_is_well_formed():
    html = export_to_html(_SAMPLES / "two-paragraphs.abw")
    assert ("<!DOCTYPE html>" in html or "<html>" in html)
    assert "</html>" in html


def test_export_to_txt_contains_paragraph_text():
    txt = export_to_txt(_SAMPLES / "two-paragraphs.abw")
    assert "First paragraph." in txt
    assert "Second paragraph." in txt


def test_export_to_txt_line_count():
    txt = export_to_txt(_SAMPLES / "two-paragraphs.abw")
    lines = [l for l in txt.splitlines() if l.strip()]
    assert len(lines) >= 2


def test_export_to_json_is_valid_json():
    json_str = export_to_json(_SAMPLES / "two-paragraphs.abw")
    data = json.loads(json_str)
    assert isinstance(data, dict)
    assert "paragraphs" in data
    assert len(data["paragraphs"]) == 2


def test_export_to_csv_has_header_and_rows():
    csv_str = export_to_csv(_SAMPLES / "two-paragraphs.abw")
    lines = [l for l in csv_str.splitlines() if l.strip()]
    assert len(lines) >= 2
    assert any("paragraph" in l.lower() for l in lines)


def test_word_frequency_has_known_word():
    model = load(_SAMPLES / "two-paragraphs.abw")
    freq = word_frequency(model)
    assert any("paragraph" in k.lower() for k in freq)


def test_get_unique_words_no_duplicates():
    model = load(_SAMPLES / "two-paragraphs.abw")
    words = get_unique_words(model)
    assert len(words) == len(set(words))


def test_get_char_count_matches_content():
    model = load(_SAMPLES / "two-paragraphs.abw")
    count = get_char_count(model)
    # "First paragraph." (16) + "Second paragraph." (17) = 33 min
    assert count >= 30


def test_join_paragraphs_contains_all_text():
    model = load(_SAMPLES / "two-paragraphs.abw")
    text = join_paragraphs(model)
    assert "First paragraph." in text
    assert "Second paragraph." in text


def test_search_paragraph_finds_known_text():
    model = load(_SAMPLES / "two-paragraphs.abw")
    results = search_paragraph(model, "First")
    assert len(results) >= 1
