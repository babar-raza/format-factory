"""
Dogfood pipeline: FODT remaining + FODP remaining → NDJSON export.
Covers FODT: fodt_words_per_sentence
Covers FODP: fodp_text_length_variance, fodp_slide_text_lengths, fodp_avg_title_length, fodp_is_text_heavy
Covers TSV: tsv_avg_row_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_words_per_sentence
from fodp.fodp_codec import (
    fodp_text_length_variance,
    fodp_slide_text_lengths,
    fodp_avg_title_length,
    fodp_is_text_heavy,
)
from tsv.tsv_parser import tsv_avg_row_length
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _fodt_with_paragraphs():
    return str(next(f for f in sorted(_FODT_DIR.glob("*.fodt")) if "heading" in f.name or "paragraph" in f.name))


def _valid_fodp():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


def _multi_tsv():
    return str(_TSV_DIR / "multi-column.tsv")


def test_fodt_words_per_sentence_returns_float(tmp_path):
    path = _fodt_with_paragraphs()
    result = fodt_words_per_sentence(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "fodt", "function": "fodt_words_per_sentence", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodp_text_length_variance_returns_float(tmp_path):
    path = _valid_fodp()
    result = fodp_text_length_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "fodp", "function": "fodp_text_length_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodp_slide_text_lengths_returns_list(tmp_path):
    path = _valid_fodp()
    result = fodp_slide_text_lengths(path)
    assert isinstance(result, list)

    record = {"format": "fodp", "function": "fodp_slide_text_lengths", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_avg_title_length_returns_float(tmp_path):
    path = _valid_fodp()
    result = fodp_avg_title_length(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "fodp", "function": "fodp_avg_title_length", "avg": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodp_is_text_heavy_returns_bool(tmp_path):
    path = _valid_fodp()
    result = fodp_is_text_heavy(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_is_text_heavy", "is_text_heavy": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_text_heavy"], bool)
    assert json.dumps(loaded[0]) is not None


def test_tsv_avg_row_length_returns_float(tmp_path):
    path = _multi_tsv()
    result = tsv_avg_row_length(path)
    assert isinstance(result, float)
    assert result >= 1.0

    record = {"format": "tsv", "function": "tsv_avg_row_length", "avg": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 1.0
    assert json.dumps(loaded[0]) is not None
