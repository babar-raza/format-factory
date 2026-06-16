"""
Dogfood pipeline: ABW remaining 3 + SYLK remaining → NDJSON export.
Covers: abw_empty_paragraph_count, abw_has_content, abw_has_metadata,
        find_rows_by_value, add_row, delete_row (sylk)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_empty_paragraph_count, abw_has_content, abw_has_metadata
from sylk.sylk_parser import find_rows_by_value, add_row, delete_row
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _content_abw():
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if abw_has_content(str(f)):
            return str(f)
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def test_abw_empty_paragraph_count_returns_int(tmp_path):
    path = _content_abw()
    result = abw_empty_paragraph_count(path)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "abw", "function": "abw_empty_paragraph_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_has_content_returns_bool(tmp_path):
    path = _content_abw()
    result = abw_has_content(path)
    assert isinstance(result, bool)
    assert result is True
    record = {"format": "abw", "function": "abw_has_content", "has_content": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["has_content"] is True
    assert json.dumps(loaded[0]) is not None


def test_abw_has_metadata_returns_bool(tmp_path):
    path = _content_abw()
    result = abw_has_metadata(path)
    assert isinstance(result, bool)
    record = {"format": "abw", "function": "abw_has_metadata", "has_metadata": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_metadata"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_find_rows_by_value_returns_list(tmp_path):
    path = _sylk_file()
    result = find_rows_by_value(path, "Name")
    assert isinstance(result, list)
    assert len(result) >= 1
    record = {"format": "sylk", "function": "find_rows_by_value", "match_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["match_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_sylk_add_row_returns_dict(tmp_path):
    path = _sylk_file()
    dest = tmp_path / "out.slk"
    result = add_row(path, str(dest), ["NewA", "NewB"])
    assert isinstance(result, dict)
    assert dest.exists()
    record = {"format": "sylk", "function": "add_row", "ok": dest.exists()}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_sylk_delete_row_returns_dict(tmp_path):
    path = _sylk_file()
    dest = tmp_path / "out.slk"
    result = delete_row(path, str(dest), 1)
    assert isinstance(result, dict)
    assert dest.exists()
    record = {"format": "sylk", "function": "delete_row", "ok": dest.exists()}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None
