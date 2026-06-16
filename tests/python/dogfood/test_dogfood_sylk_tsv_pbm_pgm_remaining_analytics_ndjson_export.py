"""
tests/python/dogfood/test_dogfood_sylk_tsv_pbm_pgm_remaining_analytics_ndjson_export.py

Dogfood export: SYLK remaining (is_rectangular, min_row_length, has_string_cells,
unique_row_count, avg_cell_value_length) + TSV remaining (is_single_column,
is_all_numeric, unique_value_count) + PBM remaining (min_dimension, black_density,
area) + PGM remaining (min_dimension, area, mean_brightness) -> NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    sylk_is_rectangular,
    sylk_min_row_length,
    sylk_has_string_cells,
    sylk_unique_row_count,
    sylk_avg_cell_value_length,
)
from tsv.tsv_parser import (
    tsv_is_single_column,
    tsv_is_all_numeric,
    tsv_unique_value_count,
)
from pbm.pbm_parser import pbm_min_dimension, pbm_black_density, pbm_area
from pgm.pgm_parser import pgm_min_dimension, pgm_area, pgm_mean_brightness
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"
_TSV = _REPO / "samples" / "by-format" / "tsv"
_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


def test_sylk_is_rectangular_and_min_row_length(tmp_path):
    path = str(_SYLK / "minimal-2x2.slk")
    assert sylk_is_rectangular(path) is True
    assert sylk_min_row_length(path) == 2
    records = [{"file": "minimal-2x2.slk", "sylk_is_rectangular": True, "sylk_min_row_length": 2}]
    out = tmp_path / "sylk_rect.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["sylk_is_rectangular"] is True
    assert rows[0]["sylk_min_row_length"] == 2


def test_sylk_has_string_cells_and_unique_row_count(tmp_path):
    path = str(_SYLK / "minimal-2x2.slk")
    assert sylk_has_string_cells(path) is True
    assert sylk_unique_row_count(path) == 2
    records = [{"file": "minimal-2x2.slk", "has_string_cells": True, "unique_row_count": 2}]
    out = tmp_path / "sylk_cells.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["has_string_cells"] is True
    assert rows[0]["unique_row_count"] == 2


def test_sylk_avg_cell_value_length(tmp_path):
    path = str(_SYLK / "minimal-2x2.slk")
    avg = sylk_avg_cell_value_length(path)
    assert avg == 4.0
    record = {"file": "minimal-2x2.slk", "sylk_avg_cell_value_length": avg}
    out = tmp_path / "sylk_avg.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["sylk_avg_cell_value_length"] == 4.0


def test_tsv_is_single_column_and_is_all_numeric(tmp_path):
    path = str(_TSV / "minimal-2x2.tsv")
    assert tsv_is_single_column(path) is False
    assert tsv_is_all_numeric(path) is False
    records = [{"file": "minimal-2x2.tsv", "tsv_is_single_column": False, "tsv_is_all_numeric": False}]
    out = tmp_path / "tsv_col.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["tsv_is_single_column"] is False
    assert rows[0]["tsv_is_all_numeric"] is False


def test_tsv_unique_value_count(tmp_path):
    path = str(_TSV / "minimal-2x2.tsv")
    count = tsv_unique_value_count(path)
    assert count == 4
    record = {"file": "minimal-2x2.tsv", "tsv_unique_value_count": count}
    out = tmp_path / "tsv_unique.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["tsv_unique_value_count"] == 4


def test_pbm_min_dimension_black_density_area(tmp_path):
    path = str(_PBM / "1x1-black.pbm")
    path2 = str(_PBM / "2x2-checker.pbm")
    assert pbm_min_dimension(path) == 1
    assert pbm_black_density(path) == 1.0
    assert pbm_area(path) == 1
    assert pbm_area(path2) == 4
    records = [
        {"file": "1x1-black.pbm", "pbm_min_dimension": 1, "pbm_black_density": 1.0, "pbm_area": 1},
        {"file": "2x2-checker.pbm", "pbm_area": 4},
    ]
    out = tmp_path / "pbm_remaining.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["pbm_min_dimension"] == 1
    assert rows[0]["pbm_black_density"] == 1.0
    assert rows[1]["pbm_area"] == 4


def test_pgm_min_dimension_area_mean_brightness(tmp_path):
    path = str(_PGM / "2x2-gradient.pgm")
    assert pgm_min_dimension(path) == 2
    assert pgm_area(path) == 4
    assert pgm_mean_brightness(path) == 127.5
    records = [
        {"file": "2x2-gradient.pgm", "pgm_min_dimension": 2,
         "pgm_area": 4, "pgm_mean_brightness": 127.5},
    ]
    out = tmp_path / "pgm_remaining.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["pgm_min_dimension"] == 2
    assert rows[0]["pgm_area"] == 4
    assert rows[0]["pgm_mean_brightness"] == 127.5
