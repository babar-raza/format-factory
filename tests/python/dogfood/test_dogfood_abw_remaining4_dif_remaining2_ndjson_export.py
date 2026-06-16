"""
Dogfood pipeline: ABW remaining model analytics + DIF remaining path analytics → NDJSON export.
Covers ABW: get_section_count, get_char_count, text_stats, export_to_json, get_word_count, word_frequency
Covers DIF: get_capabilities, get_row_count, get_row_values, get_column_values, sum_column, sum_row
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    load as abw_load,
    get_section_count,
    get_char_count,
    text_stats,
    export_to_json as abw_export_to_json,
    get_word_count,
    word_frequency,
    get_paragraph_count,
)
from dif.dif_parser import (
    get_capabilities as dif_get_capabilities,
    get_row_count,
    get_row_values,
    get_column_values,
    sum_column,
    sum_row,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _abw_file():
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if "invalid" not in f.name and get_paragraph_count(str(f)) > 0:
            return str(f)
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def test_abw_get_section_count_returns_int(tmp_path):
    path = _abw_file()
    result = get_section_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "get_section_count", "section_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["section_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_get_char_count_returns_int(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = get_char_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "get_char_count", "char_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["char_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_text_stats_returns_dict(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = text_stats(model)
    assert isinstance(result, dict)
    assert "paragraph_count" in result

    record = {"format": "abw", "function": "text_stats", "paragraph_count": result["paragraph_count"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["paragraph_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_export_to_json_returns_str(tmp_path):
    path = _abw_file()
    result = abw_export_to_json(path)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)

    record = {"format": "abw", "function": "export_to_json", "is_abw": parsed.get("is_abw", False)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_abw"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_get_word_count_returns_int(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = get_word_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "get_word_count", "word_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["word_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_word_frequency_returns_dict(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = word_frequency(model)
    assert isinstance(result, dict)

    record = {"format": "abw", "function": "word_frequency", "unique_words": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["unique_words"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_get_capabilities_returns_dict(tmp_path):
    result = dif_get_capabilities()
    assert isinstance(result, dict)
    assert "format" in result
    assert result["format"] == "dif"

    record = {"format": "dif", "function": "get_capabilities", "format_name": result["format"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format_name"] == "dif"
    assert json.dumps(loaded[0]) is not None


def test_dif_get_row_count_returns_int(tmp_path):
    path = _dif_file()
    result = get_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "get_row_count", "row_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_get_row_values_returns_list(tmp_path):
    path = _dif_file()
    result = get_row_values(path, 0)
    assert isinstance(result, list)

    record = {"format": "dif", "function": "get_row_values", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_get_column_values_returns_list(tmp_path):
    path = _dif_file()
    result = get_column_values(path, 0)
    assert isinstance(result, list)

    record = {"format": "dif", "function": "get_column_values", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_sum_column_returns_float(tmp_path):
    path = _dif_file()
    result = sum_column(path, 0)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "sum_column", "total": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["total"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_dif_sum_row_returns_float(tmp_path):
    path = _dif_file()
    result = sum_row(path, 0)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "sum_row", "total": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["total"], (int, float))
    assert json.dumps(loaded[0]) is not None
