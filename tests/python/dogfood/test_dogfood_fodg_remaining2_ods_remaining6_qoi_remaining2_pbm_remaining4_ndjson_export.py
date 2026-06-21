"""
Dogfood pipeline: FODG remaining + ODS remaining + QOI remaining + PBM remaining -> NDJSON export.
Covers FODG: fodg_avg_shapes_per_nonempty_page, fodg_avg_text_per_shape
Covers ODS: ods_avg_nonempty_cells_per_sheet, ods_column_fill_rate, ods_file_size_bytes,
            ods_max_sheet_cell_count, ods_min_sheet_cell_count, ods_unique_value_count
Covers QOI: qoi_blue_channel_avg, qoi_green_channel_avg
Covers PBM: pbm_black_exceeds_white, pbm_center_pixel_value
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    fodg_avg_shapes_per_nonempty_page,
    fodg_avg_text_per_shape,
)
from ods.ods_parser import (
    ods_avg_nonempty_cells_per_sheet,
    ods_column_fill_rate,
    ods_file_size_bytes,
    ods_max_sheet_cell_count,
    ods_min_sheet_cell_count,
    ods_unique_value_count,
)
from qoi.qoi_parser import qoi_blue_channel_avg, qoi_green_channel_avg
from pbm.pbm_parser import pbm_black_exceeds_white, pbm_center_pixel_value
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _fodg_file():
    return str(next(iter(sorted(_FODG_DIR.glob("*.fodg")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def test_fodg_avg_shapes_per_nonempty_page_returns_float(tmp_path):
    path = _fodg_file()
    result = fodg_avg_shapes_per_nonempty_page(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_avg_shapes_per_nonempty_page", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_avg_text_per_shape_returns_float(tmp_path):
    path = _fodg_file()
    result = fodg_avg_text_per_shape(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_avg_text_per_shape", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_avg_nonempty_cells_per_sheet_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_nonempty_cells_per_sheet(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_avg_nonempty_cells_per_sheet", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_column_fill_rate_returns_float(tmp_path):
    path = _ods_file()
    result = ods_column_fill_rate(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_column_fill_rate", "rate": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["rate"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_file_size_bytes_returns_int(tmp_path):
    path = _ods_file()
    result = ods_file_size_bytes(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_max_sheet_cell_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_max_sheet_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_max_sheet_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_min_sheet_cell_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_min_sheet_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_min_sheet_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_unique_value_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_unique_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_unique_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_blue_channel_avg_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_blue_channel_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_blue_channel_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_green_channel_avg_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_green_channel_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_green_channel_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_black_exceeds_white_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_black_exceeds_white(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_black_exceeds_white", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pbm_center_pixel_value_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_center_pixel_value(path)
    assert isinstance(result, int)
    assert result in (0, 1)

    record = {"format": "pbm", "function": "pbm_center_pixel_value", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] in (0, 1)
    assert json.dumps(loaded[0]) is not None
