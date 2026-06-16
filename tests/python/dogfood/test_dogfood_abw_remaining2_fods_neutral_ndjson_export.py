"""
Dogfood pipeline: ABW remaining path-based + FODS neutral model → NDJSON export.
Covers: abw_average_paragraph_length, abw_char_count, abw_has_sections,
        fods_all_sheets_have_data, fods_avg_cells_per_sheet, fods_empty_cell_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_average_paragraph_length, abw_char_count, abw_has_sections
from fods.neutral_model import fods_all_sheets_have_data, fods_avg_cells_per_sheet, fods_empty_cell_count
from fods.parser import parse_fods
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _content_abw():
    for f in sorted(_ABW_DIR.glob("*.abw")):
        from abw.abw_codec import abw_has_content
        if abw_has_content(str(f)):
            return str(f)
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def test_abw_average_paragraph_length_returns_float(tmp_path):
    path = _content_abw()
    result = abw_average_paragraph_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "abw", "function": "abw_average_paragraph_length", "avg_length": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_length"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_abw_char_count_returns_int(tmp_path):
    path = _content_abw()
    result = abw_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_char_count", "char_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["char_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_has_sections_returns_bool(tmp_path):
    path = _content_abw()
    result = abw_has_sections(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_sections", "has_sections": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_sections"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_all_sheets_have_data_returns_bool(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_all_sheets_have_data(model)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_all_sheets_have_data", "all_have_data": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["all_have_data"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_avg_cells_per_sheet_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_avg_cells_per_sheet(model)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "fods", "function": "fods_avg_cells_per_sheet", "avg_cells": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_cells"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fods_empty_cell_count_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_empty_cell_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_empty_cell_count", "empty_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["empty_count"] >= 0
    assert json.dumps(loaded[0]) is not None
