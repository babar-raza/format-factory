"""
Dogfood pipeline: ABW remaining ops 2 → NDJSON export.
Covers: search_replace_paragraph, reverse_paragraphs, word_wrap, get_paragraphs,
        abw_words_per_sentence, abw_paragraph_length_variance
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    load,
    search_replace_paragraph,
    reverse_paragraphs,
    word_wrap,
    get_paragraphs,
    abw_words_per_sentence,
    abw_paragraph_length_variance,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _two_para_abw():
    return str(next(f for f in sorted(_ABW_DIR.glob("*.abw")) if "two" in f.name or "paragraph" in f.name))


def test_search_replace_paragraph_returns_dict(tmp_path):
    path = _two_para_abw()
    model = load(path)
    result = search_replace_paragraph(model, "First", "Updated")
    assert isinstance(result, dict)
    assert "Updated" in result.get("paragraphs", [""])[0]

    record = {"format": "abw", "function": "search_replace_paragraph", "replaced": True}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["replaced"] is True
    assert json.dumps(loaded[0]) is not None


def test_reverse_paragraphs_returns_dict(tmp_path):
    path = _two_para_abw()
    model = load(path)
    original = model.get("paragraphs", [])
    result = reverse_paragraphs(model)
    assert isinstance(result, dict)
    reversed_paras = result.get("paragraphs", [])
    assert reversed_paras[0] == original[-1]

    record = {"format": "abw", "function": "reverse_paragraphs", "count": len(reversed_paras)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_word_wrap_returns_dict(tmp_path):
    path = _two_para_abw()
    model = load(path)
    result = word_wrap(model, 5)
    assert isinstance(result, dict)
    wrapped = result.get("paragraphs", [])
    assert len(wrapped) >= 1

    record = {"format": "abw", "function": "word_wrap", "para_count": len(wrapped)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["para_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_get_paragraphs_returns_list(tmp_path):
    path = _two_para_abw()
    model = load(path)
    result = get_paragraphs(model)
    assert isinstance(result, list)
    assert len(result) >= 1

    record = {"format": "abw", "function": "get_paragraphs", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_abw_words_per_sentence_returns_float(tmp_path):
    path = _two_para_abw()
    result = abw_words_per_sentence(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "abw", "function": "abw_words_per_sentence", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_abw_paragraph_length_variance_returns_float(tmp_path):
    path = _two_para_abw()
    result = abw_paragraph_length_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "abw", "function": "abw_paragraph_length_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None
