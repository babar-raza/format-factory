"""
Dogfood pipeline: PPM parser remaining analytics → NDJSON export.
Covers: probe_ppm, get_capabilities, ppm_is_portrait, ppm_diagonal,
        ppm_is_monochrome, ppm_total_channel_sum
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import (
    probe_ppm,
    get_capabilities,
    ppm_is_portrait,
    ppm_diagonal,
    ppm_is_monochrome,
    ppm_total_channel_sum,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def test_ppm_probe_ppm_returns_dict(tmp_path):
    path = _ppm_file()
    result = probe_ppm(path)
    assert isinstance(result, dict)
    assert result.get("valid_header") is True
    assert "width" in result and "height" in result

    record = {"format": "ppm", "function": "probe_ppm", "width": result["width"], "height": result["height"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_ppm_get_capabilities_returns_dict(tmp_path):
    result = get_capabilities()
    assert isinstance(result, dict)
    assert "format" in result
    assert result["format"] == "ppm"

    record = {"format": "ppm", "function": "get_capabilities", "format_name": result["format"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format_name"] == "ppm"
    assert json.dumps(loaded[0]) is not None


def test_ppm_is_portrait_returns_bool(tmp_path):
    path = _ppm_file()
    result = ppm_is_portrait(path)
    assert isinstance(result, bool)

    record = {"format": "ppm", "function": "ppm_is_portrait", "is_portrait": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_portrait"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ppm_diagonal_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_diagonal(path)
    assert isinstance(result, (int, float))
    assert result > 0.0

    record = {"format": "ppm", "function": "ppm_diagonal", "diagonal": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["diagonal"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_ppm_is_monochrome_returns_bool(tmp_path):
    path = _ppm_file()
    result = ppm_is_monochrome(path)
    assert isinstance(result, bool)

    record = {"format": "ppm", "function": "ppm_is_monochrome", "is_monochrome": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_monochrome"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ppm_total_channel_sum_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_total_channel_sum(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_total_channel_sum", "channel_sum": int(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["channel_sum"] >= 0
    assert json.dumps(loaded[0]) is not None
