"""
Dogfood pipeline: CSV remaining ops → NDJSON export.
Covers: get_column_names, get_cell_value, count_empty_cells,
        csv_nonempty_cell_count, csv_min_numeric_value, csv_avg_row_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (
    get_column_names,
    get_cell_value,
    count_empty_cells,
    csv_nonempty_cell_count,
    csv_min_numeric_value,
    csv_avg_row_length,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson

_SAMPLE_DIR = _REPO / "samples" / "by-format" / "csv"


def _valid_csv_files():
    return sorted(f for f in _SAMPLE_DIR.glob("*.csv") if "invalid" not in f.name)


def test_get_column_names_returns_list(tmp_path):
    path = str(_valid_csv_files()[0])
    names = get_column_names(path)
    assert isinstance(names, list)
    assert len(names) > 0

    record = {"format": "csv", "function": "get_column_names", "names": names, "count": len(names)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == len(names)
    assert json.dumps(loaded[0]) is not None


def test_get_cell_value_returns_string(tmp_path):
    path = str(_valid_csv_files()[0])
    val = get_cell_value(path, 0, 0)
    assert val is None or isinstance(val, str)

    record = {"format": "csv", "function": "get_cell_value", "row": 0, "col": 0, "value": val}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row"] == 0
    assert json.dumps(loaded[0]) is not None


def test_count_empty_cells_returns_int(tmp_path):
    path = str(_valid_csv_files()[0])
    col_names = get_column_names(path)
    assert len(col_names) > 0
    count = count_empty_cells(path, col_names[0])
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "csv", "function": "count_empty_cells", "col": col_names[0], "empty_count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["empty_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_nonempty_cell_count(tmp_path):
    path = str(_valid_csv_files()[0])
    count = csv_nonempty_cell_count(path)
    assert isinstance(count, int)
    assert count > 0

    record = {"format": "csv", "function": "csv_nonempty_cell_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] > 0
    assert json.dumps(loaded[0]) is not None


def test_csv_min_numeric_value(tmp_path):
    path = str(_valid_csv_files()[0])
    min_val = csv_min_numeric_value(path)
    assert min_val is None or isinstance(min_val, (int, float))

    record = {"format": "csv", "function": "csv_min_numeric_value", "min": min_val}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["min"] is None or isinstance(loaded[0]["min"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_csv_avg_row_length(tmp_path):
    path = str(_valid_csv_files()[0])
    avg = csv_avg_row_length(path)
    assert isinstance(avg, float)
    assert avg > 0.0

    record = {"format": "csv", "function": "csv_avg_row_length", "avg_row_length": avg}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_row_length"] > 0.0
    assert json.dumps(loaded[0]) is not None
