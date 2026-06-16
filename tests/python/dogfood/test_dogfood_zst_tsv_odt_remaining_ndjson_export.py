"""
Dogfood pipeline: ZST remaining + TSV remaining + ODT remaining → NDJSON export.
Covers: zst_frame_median_size, zst_is_large_file, parse_tsv_strict,
        tsv_max_field_count, tsv_is_multi_row, odt_list_density
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import zst_frame_median_size, zst_is_large_file
from tsv.tsv_parser import parse_tsv_strict, tsv_max_field_count, tsv_is_multi_row
from odt.odt_parser import odt_list_density
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _zst_file():
    return str(next(iter(sorted(_ZST_DIR.glob("*.zst")))))


def _tsv_file():
    return str(next(f for f in sorted(_TSV_DIR.glob("*.tsv")) if "multi" in f.name or "column" in f.name))


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def test_zst_frame_median_size_returns_numeric(tmp_path):
    path = _zst_file()
    result = zst_frame_median_size(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "zst", "function": "zst_frame_median_size", "median_size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["median_size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_zst_is_large_file_returns_bool(tmp_path):
    path = _zst_file()
    result = zst_is_large_file(path)
    assert isinstance(result, bool)

    record = {"format": "zst", "function": "zst_is_large_file", "is_large": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_large"], bool)
    assert json.dumps(loaded[0]) is not None


def test_parse_tsv_strict_returns_dict(tmp_path):
    path = _tsv_file()
    result = parse_tsv_strict(path)
    assert isinstance(result, dict)
    assert result.get("format") == "tsv" or result.get("row_count") is not None

    record = {"format": "tsv", "function": "parse_tsv_strict", "row_count": result.get("row_count", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_max_field_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_max_field_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "tsv", "function": "tsv_max_field_count", "max_fields": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["max_fields"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_tsv_is_multi_row_returns_bool(tmp_path):
    path = _tsv_file()
    result = tsv_is_multi_row(path)
    assert isinstance(result, bool)
    assert result is True

    record = {"format": "tsv", "function": "tsv_is_multi_row", "is_multi_row": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_multi_row"] is True
    assert json.dumps(loaded[0]) is not None


def test_odt_list_density_returns_float(tmp_path):
    path = _odt_file()
    result = odt_list_density(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "odt", "function": "odt_list_density", "list_density": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["list_density"] >= 0.0
    assert json.dumps(loaded[0]) is not None
