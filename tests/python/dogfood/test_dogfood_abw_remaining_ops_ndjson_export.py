"""
Dogfood pipeline: ABW remaining ops → NDJSON export.
Covers: search_paragraph, edit_paragraph, get_paragraph_at, shortest_paragraph,
        merge_abw, truncate_paragraphs
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
    search_paragraph,
    edit_paragraph,
    get_paragraph_at,
    shortest_paragraph,
    merge_abw,
    truncate_paragraphs,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _two_para_abw():
    return str(next(f for f in sorted(_ABW_DIR.glob("*.abw")) if "two" in f.name or "paragraph" in f.name))


def test_search_paragraph_returns_list(tmp_path):
    path = _two_para_abw()
    model = load(path)
    results = search_paragraph(model, "First", case_sensitive=True)
    assert isinstance(results, list)
    assert len(results) >= 1
    assert results[0] == 0

    record = {"format": "abw", "function": "search_paragraph", "query": "First", "match_count": len(results)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["match_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_edit_paragraph_returns_dict(tmp_path):
    path = _two_para_abw()
    model = load(path)
    result = edit_paragraph(model, 0, "Updated content.")
    assert isinstance(result, dict)
    assert result.get("paragraphs", [""])[0] == "Updated content."

    record = {"format": "abw", "function": "edit_paragraph", "index": 0, "new_text": "Updated content."}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["new_text"] == "Updated content."
    assert json.dumps(loaded[0]) is not None


def test_get_paragraph_at_returns_str(tmp_path):
    path = _two_para_abw()
    model = load(path)
    para = get_paragraph_at(model, 0)
    assert isinstance(para, str)
    assert len(para) > 0

    record = {"format": "abw", "function": "get_paragraph_at", "index": 0, "length": len(para)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] > 0
    assert json.dumps(loaded[0]) is not None


def test_shortest_paragraph_returns_str(tmp_path):
    path = _two_para_abw()
    model = load(path)
    result = shortest_paragraph(model)
    assert isinstance(result, str)
    assert len(result) > 0

    record = {"format": "abw", "function": "shortest_paragraph", "length": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] > 0
    assert json.dumps(loaded[0]) is not None


def test_merge_abw_returns_dict(tmp_path):
    path = _two_para_abw()
    model_a = load(path)
    model_b = load(path)
    result = merge_abw(model_a, model_b)
    assert isinstance(result, dict)
    count_a = model_a.get("paragraph_count", len(model_a.get("paragraphs", [])))
    count_b = model_b.get("paragraph_count", len(model_b.get("paragraphs", [])))
    merged_count = result.get("paragraph_count", len(result.get("paragraphs", [])))
    assert merged_count == count_a + count_b

    record = {"format": "abw", "function": "merge_abw", "merged_paragraph_count": merged_count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["merged_paragraph_count"] >= 2
    assert json.dumps(loaded[0]) is not None


def test_truncate_paragraphs_returns_dict(tmp_path):
    path = _two_para_abw()
    model = load(path)
    result = truncate_paragraphs(model, 1)
    assert isinstance(result, dict)
    para_count = result.get("paragraph_count", len(result.get("paragraphs", [])))
    assert para_count == 1

    record = {"format": "abw", "function": "truncate_paragraphs", "n": 1, "result_count": para_count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["result_count"] == 1
    assert json.dumps(loaded[0]) is not None
