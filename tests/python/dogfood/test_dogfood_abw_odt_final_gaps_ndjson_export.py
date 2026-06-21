"""Dogfood export: ABW(4) + ODT(3) final analytics gap functions → NDJSON.

Functions covered (previously uncovered):
  ABW: abw_para_char_variance, abw_uppercase_count, abw_vowel_ratio, abw_word_length_variance
  ODT: odt_has_multiple_paragraphs, odt_min_paragraph_words, odt_unique_ratio

Note: abw_sentence_avg_length and abw_uppercase_word_count have AttributeError on the
minimal sample (paragraphs list contains strings, not dicts) — excluded from this batch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from abw.abw_codec import (
    abw_para_char_variance,
    abw_uppercase_count,
    abw_vowel_ratio,
    abw_word_length_variance,
)
from odt.odt_parser import (
    odt_has_multiple_paragraphs,
    odt_min_paragraph_words,
    odt_unique_ratio,
)

_ABW = str(_REPO / "samples" / "by-format" / "abw" / "minimal-document.abw")
_ODT = str(_REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt")


# --- ABW tests ---

def test_abw_para_char_variance(tmp_path):
    val = abw_para_char_variance(_ABW)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "abw_para_char_variance.ndjson"
    write_ndjson([{"metric": "abw_para_char_variance", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_abw_uppercase_count(tmp_path):
    val = abw_uppercase_count(_ABW)
    assert isinstance(val, int)
    assert val == 1
    out = tmp_path / "abw_uppercase_count.ndjson"
    write_ndjson([{"metric": "abw_uppercase_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1


def test_abw_vowel_ratio(tmp_path):
    val = abw_vowel_ratio(_ABW)
    assert isinstance(val, float)
    assert val == 0.4
    out = tmp_path / "abw_vowel_ratio.ndjson"
    write_ndjson([{"metric": "abw_vowel_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.4


def test_abw_word_length_variance(tmp_path):
    val = abw_word_length_variance(_ABW)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "abw_word_length_variance.ndjson"
    write_ndjson([{"metric": "abw_word_length_variance", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


# --- ODT tests ---

def test_odt_has_multiple_paragraphs(tmp_path):
    val = odt_has_multiple_paragraphs(_ODT)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "odt_has_multiple_paragraphs.ndjson"
    write_ndjson([{"metric": "odt_has_multiple_paragraphs", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


def test_odt_min_paragraph_words(tmp_path):
    val = odt_min_paragraph_words(_ODT)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "odt_min_paragraph_words.ndjson"
    write_ndjson([{"metric": "odt_min_paragraph_words", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_odt_unique_ratio(tmp_path):
    val = odt_unique_ratio(_ODT)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "odt_unique_ratio.ndjson"
    write_ndjson([{"metric": "odt_unique_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_abw_odt_batch_ndjson_export(tmp_path):
    records = [
        {"fmt": "abw", "metric": "abw_para_char_variance", "value": abw_para_char_variance(_ABW)},
        {"fmt": "abw", "metric": "abw_uppercase_count", "value": abw_uppercase_count(_ABW)},
        {"fmt": "abw", "metric": "abw_vowel_ratio", "value": abw_vowel_ratio(_ABW)},
        {"fmt": "abw", "metric": "abw_word_length_variance", "value": abw_word_length_variance(_ABW)},
        {"fmt": "odt", "metric": "odt_has_multiple_paragraphs", "value": odt_has_multiple_paragraphs(_ODT)},
        {"fmt": "odt", "metric": "odt_min_paragraph_words", "value": odt_min_paragraph_words(_ODT)},
        {"fmt": "odt", "metric": "odt_unique_ratio", "value": odt_unique_ratio(_ODT)},
    ]
    out = tmp_path / "abw_odt_final_gaps.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 7
    parsed = [json.loads(ln) for ln in lines]
    fmts = {r["fmt"] for r in parsed}
    assert "abw" in fmts
    assert "odt" in fmts
