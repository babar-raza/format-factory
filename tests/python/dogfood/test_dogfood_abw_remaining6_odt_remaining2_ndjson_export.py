"""
Dogfood pipeline: ABW remaining analytics + ODT remaining analytics → NDJSON export.
Covers ABW: abw_is_content_rich, abw_avg_chars_per_word, abw_whitespace_ratio,
            abw_avg_sentence_length, abw_longest_paragraph_words, abw_longest_paragraph_index
Covers ODT: parse_odt_strict, odt_heading_per_paragraph, odt_is_content_rich,
            odt_numeric_value_sum, odt_unique_char_count, abw_unique_char_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_is_content_rich,
    abw_avg_chars_per_word,
    abw_whitespace_ratio,
    abw_avg_sentence_length,
    abw_longest_paragraph_words,
    abw_longest_paragraph_index,
)
from odt.odt_parser import (
    parse_odt_strict,
    odt_heading_per_paragraph,
    odt_is_content_rich,
    odt_numeric_value_sum,
    odt_unique_char_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _abw_file():
    # Use two-paragraphs.abw which has actual content
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if "two-paragraphs" in f.name:
            return str(f)
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def test_abw_is_content_rich_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_is_content_rich(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_is_content_rich", "is_rich": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_rich"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_chars_per_word_returns_float(tmp_path):
    path = _abw_file()
    result = abw_avg_chars_per_word(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_chars_per_word", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_whitespace_ratio_returns_float(tmp_path):
    path = _abw_file()
    result = abw_whitespace_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "abw", "function": "abw_whitespace_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_sentence_length_returns_float(tmp_path):
    path = _abw_file()
    result = abw_avg_sentence_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_sentence_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_longest_paragraph_words_returns_int(tmp_path):
    path = _abw_file()
    result = abw_longest_paragraph_words(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_longest_paragraph_words", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_longest_paragraph_index_returns_int(tmp_path):
    path = _abw_file()
    result = abw_longest_paragraph_index(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_longest_paragraph_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["index"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_parse_strict_returns_document(tmp_path):
    path = _odt_file()
    result = parse_odt_strict(path)
    assert hasattr(result, "paragraphs")
    assert hasattr(result, "path")

    record = {"format": "odt", "function": "parse_odt_strict", "para_count": len(result.paragraphs)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["para_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_heading_per_paragraph_returns_float(tmp_path):
    path = _odt_file()
    result = odt_heading_per_paragraph(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "odt", "function": "odt_heading_per_paragraph", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_is_content_rich_returns_bool(tmp_path):
    path = _odt_file()
    result = odt_is_content_rich(path)
    assert isinstance(result, bool)

    record = {"format": "odt", "function": "odt_is_content_rich", "is_rich": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_rich"], bool)
    assert json.dumps(loaded[0]) is not None


def test_odt_numeric_value_sum_returns_float(tmp_path):
    path = _odt_file()
    result = odt_numeric_value_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "odt", "function": "odt_numeric_value_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_odt_unique_char_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_unique_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_unique_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
