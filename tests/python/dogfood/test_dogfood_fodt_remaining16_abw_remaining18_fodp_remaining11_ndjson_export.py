"""
Dogfood pipeline: FODT remaining + ABW remaining + FODP remaining -> NDJSON export.
Covers FODT: fodt_space_count, fodt_total_content_blocks, fodt_uppercase_ratio,
             fodt_vowel_count, fodt_word_count_variance
Covers ABW: abw_avg_word_per_paragraph, abw_has_punctuation, abw_longest_paragraph_chars,
            abw_shortest_paragraph_chars, abw_word_length_max
Covers FODP: fodp_shape_density, fodp_slide_word_count_total
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import (
    fodt_space_count,
    fodt_total_content_blocks,
    fodt_uppercase_ratio,
    fodt_vowel_count,
    fodt_word_count_variance,
)
from abw.abw_codec import (
    abw_avg_word_per_paragraph,
    abw_has_punctuation,
    abw_longest_paragraph_chars,
    abw_shortest_paragraph_chars,
    abw_word_length_max,
)
from fodp.fodp_codec import (
    fodp_shape_density,
    fodp_slide_word_count_total,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _abw_file():
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _fodp_file():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


# --- FODT ---

def test_fodt_space_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_space_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_space_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_total_content_blocks_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_total_content_blocks(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_total_content_blocks", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_uppercase_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_uppercase_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fodt", "function": "fodt_uppercase_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fodt_vowel_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_vowel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_vowel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_word_count_variance_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_word_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_word_count_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ABW ---

def test_abw_avg_word_per_paragraph_returns_float(tmp_path):
    path = _abw_file()
    result = abw_avg_word_per_paragraph(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_word_per_paragraph", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_has_punctuation_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_has_punctuation(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_punctuation", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_longest_paragraph_chars_returns_int(tmp_path):
    path = _abw_file()
    result = abw_longest_paragraph_chars(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_longest_paragraph_chars", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_shortest_paragraph_chars_returns_int(tmp_path):
    path = _abw_file()
    result = abw_shortest_paragraph_chars(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_shortest_paragraph_chars", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_word_length_max_returns_int(tmp_path):
    path = _abw_file()
    result = abw_word_length_max(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_word_length_max", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODP ---

def test_fodp_shape_density_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_shape_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_shape_density", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_slide_word_count_total_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_slide_word_count_total(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_slide_word_count_total", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
