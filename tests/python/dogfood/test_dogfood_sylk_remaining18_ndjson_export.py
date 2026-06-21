"""Dogfood export: 18 remaining SYLK analytics gap functions → NDJSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from sylk.sylk_parser import (
    sylk_avg_numeric_sum_per_row,
    sylk_cell_row_count_variance,
    sylk_cell_sparsity,
    sylk_cells_to_rows_ratio,
    sylk_distinct_column_count,
    sylk_is_wider_than_tall,
    sylk_max_cell_text_length,
    sylk_min_cell_text_length,
    sylk_min_column_sum,
    sylk_nonempty_col_count,
    sylk_numeric_cell_sum,
    sylk_numeric_to_string_ratio,
    sylk_row_col_ratio,
    sylk_row_density_avg,
    sylk_string_cells_exceed_numeric,
    sylk_string_length_sum,
    sylk_value_type_variety,
    sylk_value_variance,
)

_SYLK = str(_REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk")


def _w(tmp_path, metric, val):
    out = tmp_path / f"{metric}.ndjson"
    write_ndjson([{"metric": metric, "value": val}], str(out))
    return json.loads(out.read_text().strip())["value"]


def test_sylk_avg_numeric_sum_per_row(tmp_path):
    val = sylk_avg_numeric_sum_per_row(_SYLK)
    assert isinstance(val, float) and val == 6.0
    assert _w(tmp_path, "sylk_avg_numeric_sum_per_row", val) == 6.0


def test_sylk_cell_row_count_variance(tmp_path):
    val = sylk_cell_row_count_variance(_SYLK)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "sylk_cell_row_count_variance", val) == 0.0


def test_sylk_cell_sparsity(tmp_path):
    val = sylk_cell_sparsity(_SYLK)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "sylk_cell_sparsity", val) == 0.0


def test_sylk_cells_to_rows_ratio(tmp_path):
    val = sylk_cells_to_rows_ratio(_SYLK)
    assert isinstance(val, float) and val == 3.0
    assert _w(tmp_path, "sylk_cells_to_rows_ratio", val) == 3.0


def test_sylk_distinct_column_count(tmp_path):
    val = sylk_distinct_column_count(_SYLK)
    assert isinstance(val, int) and val == 3
    assert _w(tmp_path, "sylk_distinct_column_count", val) == 3


def test_sylk_is_wider_than_tall(tmp_path):
    val = sylk_is_wider_than_tall(_SYLK)
    assert isinstance(val, bool) and val is True
    assert _w(tmp_path, "sylk_is_wider_than_tall", val) is True


def test_sylk_max_cell_text_length(tmp_path):
    val = sylk_max_cell_text_length(_SYLK)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "sylk_max_cell_text_length", val) == 1


def test_sylk_min_cell_text_length(tmp_path):
    val = sylk_min_cell_text_length(_SYLK)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "sylk_min_cell_text_length", val) == 1


def test_sylk_min_column_sum(tmp_path):
    val = sylk_min_column_sum(_SYLK)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "sylk_min_column_sum", val) == 1.0


def test_sylk_nonempty_col_count(tmp_path):
    val = sylk_nonempty_col_count(_SYLK)
    assert isinstance(val, int) and val == 3
    assert _w(tmp_path, "sylk_nonempty_col_count", val) == 3


def test_sylk_numeric_cell_sum(tmp_path):
    val = sylk_numeric_cell_sum(_SYLK)
    assert isinstance(val, float) and val == 6.0
    assert _w(tmp_path, "sylk_numeric_cell_sum", val) == 6.0


def test_sylk_numeric_to_string_ratio(tmp_path):
    val = sylk_numeric_to_string_ratio(_SYLK)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "sylk_numeric_to_string_ratio", val) == 0.0


def test_sylk_row_col_ratio(tmp_path):
    val = sylk_row_col_ratio(_SYLK)
    assert isinstance(val, float)
    assert abs(val - 1.0 / 3.0) < 1e-9
    result = _w(tmp_path, "sylk_row_col_ratio", val)
    assert abs(result - 1.0 / 3.0) < 1e-9


def test_sylk_row_density_avg(tmp_path):
    val = sylk_row_density_avg(_SYLK)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "sylk_row_density_avg", val) == 1.0


def test_sylk_string_cells_exceed_numeric(tmp_path):
    val = sylk_string_cells_exceed_numeric(_SYLK)
    assert isinstance(val, bool) and val is False
    assert _w(tmp_path, "sylk_string_cells_exceed_numeric", val) is False


def test_sylk_string_length_sum(tmp_path):
    val = sylk_string_length_sum(_SYLK)
    assert isinstance(val, int) and val == 0
    assert _w(tmp_path, "sylk_string_length_sum", val) == 0


def test_sylk_value_type_variety(tmp_path):
    val = sylk_value_type_variety(_SYLK)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "sylk_value_type_variety", val) == 1


def test_sylk_value_variance(tmp_path):
    val = sylk_value_variance(_SYLK)
    assert isinstance(val, float)
    assert abs(val - 2.0 / 3.0) < 1e-9
    result = _w(tmp_path, "sylk_value_variance", val)
    assert abs(result - 2.0 / 3.0) < 1e-9


def test_sylk_all18_batch_ndjson_export(tmp_path):
    records = [
        {"metric": "sylk_avg_numeric_sum_per_row", "value": sylk_avg_numeric_sum_per_row(_SYLK)},
        {"metric": "sylk_cell_sparsity", "value": sylk_cell_sparsity(_SYLK)},
        {"metric": "sylk_distinct_column_count", "value": sylk_distinct_column_count(_SYLK)},
        {"metric": "sylk_numeric_cell_sum", "value": sylk_numeric_cell_sum(_SYLK)},
        {"metric": "sylk_value_variance", "value": sylk_value_variance(_SYLK)},
    ]
    out = tmp_path / "sylk18.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 5
    parsed = [json.loads(ln) for ln in lines]
    metrics = {r["metric"] for r in parsed}
    assert "sylk_avg_numeric_sum_per_row" in metrics
    assert "sylk_value_variance" in metrics
