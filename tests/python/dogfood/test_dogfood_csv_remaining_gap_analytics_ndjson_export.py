"""
tests/python/dogfood/test_dogfood_csv_remaining_gap_analytics_ndjson_export.py

Dogfood export: CSV remaining gap functions (distinct_value_count, empty_cell_count,
empty_cell_ratio, min_row_length, max_numeric_value, has_empty_rows,
is_rectangular, string_density) -> NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (
    csv_distinct_value_count,
    csv_empty_cell_count,
    csv_empty_cell_ratio,
    csv_min_row_length,
    csv_max_numeric_value,
    csv_has_empty_rows,
    csv_is_rectangular,
    csv_string_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_CSV = _REPO / "samples" / "by-format" / "csv"


def test_csv_distinct_value_count(tmp_path):
    path = str(_CSV / "minimal-2x2.csv")
    count = csv_distinct_value_count(path)
    assert count == 4
    record = {"file": "minimal-2x2.csv", "csv_distinct_value_count": count}
    out = tmp_path / "csv_distinct.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["csv_distinct_value_count"] == 4


def test_csv_empty_cell_count_and_ratio(tmp_path):
    path = str(_CSV / "minimal-2x2.csv")
    assert csv_empty_cell_count(path) == 0
    assert csv_empty_cell_ratio(path) == 0.0
    records = [
        {"file": "minimal-2x2.csv", "empty_cell_count": 0, "empty_cell_ratio": 0.0},
    ]
    out = tmp_path / "csv_empty.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["empty_cell_count"] == 0
    assert rows[0]["empty_cell_ratio"] == 0.0


def test_csv_min_row_length(tmp_path):
    path = str(_CSV / "minimal-2x2.csv")
    length = csv_min_row_length(path)
    assert length == 2
    record = {"file": "minimal-2x2.csv", "csv_min_row_length": length}
    out = tmp_path / "csv_min_row.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["csv_min_row_length"] == 2


def test_csv_max_numeric_value(tmp_path):
    path = str(_CSV / "minimal-2x2.csv")
    val = csv_max_numeric_value(path)
    assert val == 30.0
    record = {"file": "minimal-2x2.csv", "csv_max_numeric_value": float(val)}
    out = tmp_path / "csv_max_num.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["csv_max_numeric_value"] == 30.0


def test_csv_has_empty_rows_and_is_rectangular(tmp_path):
    path = str(_CSV / "minimal-2x2.csv")
    assert csv_has_empty_rows(path) is False
    assert csv_is_rectangular(path) is True
    records = [
        {"file": "minimal-2x2.csv", "has_empty_rows": False, "is_rectangular": True},
    ]
    out = tmp_path / "csv_shape.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["has_empty_rows"] is False
    assert rows[0]["is_rectangular"] is True


def test_csv_string_density(tmp_path):
    path = str(_CSV / "minimal-2x2.csv")
    density = csv_string_density(path)
    assert density == 0.5
    record = {"file": "minimal-2x2.csv", "csv_string_density": density}
    out = tmp_path / "csv_str_density.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["csv_string_density"] == 0.5
