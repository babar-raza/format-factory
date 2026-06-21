"""Dogfood export: CSV(6) + TSV(6) + DIF(6) second batch gap functions → NDJSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from src.python.csv.csv_parser import (
    csv_max_field_count_per_row,
    csv_max_row_field_count,
    csv_max_row_width,
    csv_numeric_value_sum,
    csv_row_col_ratio,
    csv_row_width_variance,
)
from tsv.tsv_parser import (
    tsv_max_row_field_count,
    tsv_nonempty_column_count,
    tsv_numeric_ratio,
    tsv_row_col_ratio,
    tsv_shortest_row_width,
    tsv_string_ratio,
)
from dif.dif_parser import (
    dif_cell_count_variance,
    dif_column_count_avg,
    dif_has_string_rows,
    dif_max_cell_text_length,
    dif_nonempty_cell_density,
    dif_numeric_cell_mean,
)

_CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")
_TSV = str(_REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv")
_DIF = str(_REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif")


# --- CSV batch 2 ---

def test_csv_max_field_count_per_row(tmp_path):
    val = csv_max_field_count_per_row(_CSV)
    assert isinstance(val, int) and val == 2
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "csv_max_field_count_per_row", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_csv_max_row_field_count(tmp_path):
    val = csv_max_row_field_count(_CSV)
    assert isinstance(val, int) and val == 2
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "csv_max_row_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_csv_max_row_width(tmp_path):
    val = csv_max_row_width(_CSV)
    assert isinstance(val, int) and val == 2
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "csv_max_row_width", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_csv_numeric_value_sum(tmp_path):
    val = csv_numeric_value_sum(_CSV)
    assert isinstance(val, float) and val == 55.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "csv_numeric_value_sum", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 55.0


def test_csv_row_col_ratio(tmp_path):
    val = csv_row_col_ratio(_CSV)
    assert isinstance(val, float) and val == 1.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "csv_row_col_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_csv_row_width_variance(tmp_path):
    val = csv_row_width_variance(_CSV)
    assert isinstance(val, float) and val == 0.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "csv_row_width_variance", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


# --- TSV batch 2 ---

def test_tsv_max_row_field_count(tmp_path):
    val = tsv_max_row_field_count(_TSV)
    assert isinstance(val, int) and val == 2
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "tsv_max_row_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_tsv_nonempty_column_count(tmp_path):
    val = tsv_nonempty_column_count(_TSV)
    assert isinstance(val, int) and val == 2
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "tsv_nonempty_column_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_tsv_numeric_ratio(tmp_path):
    val = tsv_numeric_ratio(_TSV)
    assert isinstance(val, float) and val == 0.5
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "tsv_numeric_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.5


def test_tsv_row_col_ratio(tmp_path):
    val = tsv_row_col_ratio(_TSV)
    assert isinstance(val, float) and val == 1.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "tsv_row_col_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_tsv_shortest_row_width(tmp_path):
    val = tsv_shortest_row_width(_TSV)
    assert isinstance(val, int) and val == 2
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "tsv_shortest_row_width", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_tsv_string_ratio(tmp_path):
    val = tsv_string_ratio(_TSV)
    assert isinstance(val, float) and val == 0.5
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "tsv_string_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.5


# --- DIF batch 2 ---

def test_dif_cell_count_variance(tmp_path):
    val = dif_cell_count_variance(_DIF)
    assert isinstance(val, float) and val == 0.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "dif_cell_count_variance", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_dif_column_count_avg(tmp_path):
    val = dif_column_count_avg(_DIF)
    assert isinstance(val, float) and val == 8.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "dif_column_count_avg", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 8.0


def test_dif_has_string_rows(tmp_path):
    val = dif_has_string_rows(_DIF)
    assert isinstance(val, bool) and val is True
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "dif_has_string_rows", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is True


def test_dif_max_cell_text_length(tmp_path):
    val = dif_max_cell_text_length(_DIF)
    assert isinstance(val, int) and val == 46
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "dif_max_cell_text_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 46


def test_dif_nonempty_cell_density(tmp_path):
    val = dif_nonempty_cell_density(_DIF)
    assert isinstance(val, float) and val == 1.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "dif_nonempty_cell_density", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_dif_numeric_cell_mean(tmp_path):
    val = dif_numeric_cell_mean(_DIF)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "out.ndjson"
    write_ndjson([{"metric": "dif_numeric_cell_mean", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_batch_ndjson_export(tmp_path):
    records = [
        {"fmt": "csv", "metric": "csv_numeric_value_sum", "value": csv_numeric_value_sum(_CSV)},
        {"fmt": "tsv", "metric": "tsv_numeric_ratio", "value": tsv_numeric_ratio(_TSV)},
        {"fmt": "dif", "metric": "dif_has_string_rows", "value": dif_has_string_rows(_DIF)},
    ]
    out = tmp_path / "batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 3
    parsed = [json.loads(ln) for ln in lines]
    fmts = {r["fmt"] for r in parsed}
    assert {"csv", "tsv", "dif"} == fmts
