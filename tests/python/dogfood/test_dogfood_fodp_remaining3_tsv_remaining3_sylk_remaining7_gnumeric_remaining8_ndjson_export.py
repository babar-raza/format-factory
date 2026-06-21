"""
Dogfood pipeline: FODP remaining batch 2 + TSV remaining + SYLK remaining + Gnumeric remaining.
Covers FODP: fodp_shape_variance, fodp_shortest_slide_index, fodp_slide_count_is_one,
             fodp_slide_text_variance, fodp_slide_title_count, fodp_total_images,
             fodp_total_text_chars, fodp_total_title_chars
Covers TSV: tsv_has_only_numeric, tsv_is_wider_than_tall
Covers SYLK: sylk_value_length_sum
Covers Gnumeric: gnumeric_avg_cell_value_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import (
    fodp_shape_variance,
    fodp_shortest_slide_index,
    fodp_slide_count_is_one,
    fodp_slide_text_variance,
    fodp_slide_title_count,
    fodp_total_images,
    fodp_total_text_chars,
    fodp_total_title_chars,
)
from tsv.tsv_parser import tsv_has_only_numeric, tsv_is_wider_than_tall
from sylk.sylk_parser import sylk_value_length_sum
from gnumeric.gnumeric_codec import gnumeric_avg_cell_value_length
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODP_FILE = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"
_TSV_FILE = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_GNUMERIC_FILE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def test_fodp_shape_variance_returns_int(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_shape_variance(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_shape_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_shortest_slide_index_returns_int(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_shortest_slide_index(path)
    assert isinstance(result, int)

    record = {"format": "fodp", "function": "fodp_shortest_slide_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["index"], int)
    assert json.dumps(loaded[0]) is not None


def test_fodp_slide_count_is_one_returns_bool(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_slide_count_is_one(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_slide_count_is_one", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_slide_text_variance_returns_float(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_slide_text_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_slide_text_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_slide_title_count_returns_int(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_slide_title_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_slide_title_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_total_images_returns_int(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_total_images(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_total_images", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_total_text_chars_returns_int(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_total_text_chars(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_total_text_chars", "chars": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["chars"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_total_title_chars_returns_int(tmp_path):
    path = str(_FODP_FILE)
    result = fodp_total_title_chars(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_total_title_chars", "chars": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["chars"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_has_only_numeric_returns_bool(tmp_path):
    path = str(_TSV_FILE)
    result = tsv_has_only_numeric(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_has_only_numeric", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_tsv_is_wider_than_tall_returns_bool(tmp_path):
    path = str(_TSV_FILE)
    result = tsv_is_wider_than_tall(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_is_wider_than_tall", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_value_length_sum_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_value_length_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_value_length_sum", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_avg_cell_value_length_returns_float(tmp_path):
    path = str(_GNUMERIC_FILE)
    result = gnumeric_avg_cell_value_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_avg_cell_value_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None
