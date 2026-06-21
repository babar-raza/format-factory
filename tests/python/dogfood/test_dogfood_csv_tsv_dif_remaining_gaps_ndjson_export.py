"""Dogfood export: CSV(8) + TSV(6) + DIF(6) analytics gap functions → NDJSON.

Functions covered (previously uncovered):
  CSV: csv_alpha_field_count, csv_distinct_col_count, csv_empty_row_ratio,
       csv_field_length_variance, csv_file_size_bytes, csv_has_only_numeric_row,
       csv_header_total_length, csv_is_single_row
  TSV: tsv_alpha_field_count, tsv_avg_field_length, tsv_empty_field_ratio,
       tsv_file_size_bytes, tsv_has_only_numeric_row, tsv_is_single_row
  DIF: dif_avg_cell_text_length, dif_avg_numeric_value, dif_cell_value_length_sum,
       dif_column_type_variety, dif_file_size_bytes, dif_has_string_cells
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson

# CSV: use src.python path to avoid stdlib 'csv' module conflict
from src.python.csv.csv_parser import (
    csv_alpha_field_count,
    csv_distinct_col_count,
    csv_empty_row_ratio,
    csv_field_length_variance,
    csv_file_size_bytes,
    csv_has_only_numeric_row,
    csv_header_total_length,
    csv_is_single_row,
)
from tsv.tsv_parser import (
    tsv_alpha_field_count,
    tsv_avg_field_length,
    tsv_empty_field_ratio,
    tsv_file_size_bytes,
    tsv_has_only_numeric_row,
    tsv_is_single_row,
)
from dif.dif_parser import (
    dif_avg_cell_text_length,
    dif_avg_numeric_value,
    dif_cell_value_length_sum,
    dif_column_type_variety,
    dif_file_size_bytes,
    dif_has_string_cells,
)

_CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")
_TSV = str(_REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv")
_DIF = str(_REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif")


# --- CSV tests ---

def test_csv_alpha_field_count(tmp_path):
    val = csv_alpha_field_count(_CSV)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "csv_alpha_field_count.ndjson"
    write_ndjson([{"metric": "csv_alpha_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_csv_distinct_col_count(tmp_path):
    val = csv_distinct_col_count(_CSV)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "csv_distinct_col_count.ndjson"
    write_ndjson([{"metric": "csv_distinct_col_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_csv_empty_row_ratio(tmp_path):
    val = csv_empty_row_ratio(_CSV)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "csv_empty_row_ratio.ndjson"
    write_ndjson([{"metric": "csv_empty_row_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_csv_field_length_variance(tmp_path):
    val = csv_field_length_variance(_CSV)
    assert isinstance(val, float)
    assert val == 1.5
    out = tmp_path / "csv_field_length_variance.ndjson"
    write_ndjson([{"metric": "csv_field_length_variance", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.5


def test_csv_file_size_bytes(tmp_path):
    val = csv_file_size_bytes(_CSV)
    assert isinstance(val, int)
    assert val == 25
    out = tmp_path / "csv_file_size_bytes.ndjson"
    write_ndjson([{"metric": "csv_file_size_bytes", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 25


def test_csv_has_only_numeric_row(tmp_path):
    val = csv_has_only_numeric_row(_CSV)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "csv_has_only_numeric_row.ndjson"
    write_ndjson([{"metric": "csv_has_only_numeric_row", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


def test_csv_header_total_length(tmp_path):
    val = csv_header_total_length(_CSV)
    assert isinstance(val, int)
    assert val == 7
    out = tmp_path / "csv_header_total_length.ndjson"
    write_ndjson([{"metric": "csv_header_total_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 7


def test_csv_is_single_row(tmp_path):
    val = csv_is_single_row(_CSV)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "csv_is_single_row.ndjson"
    write_ndjson([{"metric": "csv_is_single_row", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


# --- TSV tests ---

def test_tsv_alpha_field_count(tmp_path):
    val = tsv_alpha_field_count(_TSV)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "tsv_alpha_field_count.ndjson"
    write_ndjson([{"metric": "tsv_alpha_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_tsv_avg_field_length(tmp_path):
    val = tsv_avg_field_length(_TSV)
    assert isinstance(val, float)
    assert val == 3.0
    out = tmp_path / "tsv_avg_field_length.ndjson"
    write_ndjson([{"metric": "tsv_avg_field_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 3.0


def test_tsv_empty_field_ratio(tmp_path):
    val = tsv_empty_field_ratio(_TSV)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "tsv_empty_field_ratio.ndjson"
    write_ndjson([{"metric": "tsv_empty_field_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_tsv_file_size_bytes(tmp_path):
    val = tsv_file_size_bytes(_TSV)
    assert isinstance(val, int)
    assert val == 28
    out = tmp_path / "tsv_file_size_bytes.ndjson"
    write_ndjson([{"metric": "tsv_file_size_bytes", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 28


def test_tsv_has_only_numeric_row(tmp_path):
    val = tsv_has_only_numeric_row(_TSV)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "tsv_has_only_numeric_row.ndjson"
    write_ndjson([{"metric": "tsv_has_only_numeric_row", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


def test_tsv_is_single_row(tmp_path):
    val = tsv_is_single_row(_TSV)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "tsv_is_single_row.ndjson"
    write_ndjson([{"metric": "tsv_is_single_row", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


# --- DIF tests ---

def test_dif_avg_cell_text_length(tmp_path):
    val = dif_avg_cell_text_length(_DIF)
    assert isinstance(val, float)
    assert val == 4.5
    out = tmp_path / "dif_avg_cell_text_length.ndjson"
    write_ndjson([{"metric": "dif_avg_cell_text_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 4.5


def test_dif_avg_numeric_value(tmp_path):
    val = dif_avg_numeric_value(_DIF)
    assert isinstance(val, float)
    assert val == 70.5
    out = tmp_path / "dif_avg_numeric_value.ndjson"
    write_ndjson([{"metric": "dif_avg_numeric_value", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 70.5


def test_dif_cell_value_length_sum(tmp_path):
    val = dif_cell_value_length_sum(_DIF)
    assert isinstance(val, int)
    assert val == 342
    out = tmp_path / "dif_cell_value_length_sum.ndjson"
    write_ndjson([{"metric": "dif_cell_value_length_sum", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 342


def test_dif_column_type_variety(tmp_path):
    val = dif_column_type_variety(_DIF)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "dif_column_type_variety.ndjson"
    write_ndjson([{"metric": "dif_column_type_variety", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_dif_file_size_bytes(tmp_path):
    val = dif_file_size_bytes(_DIF)
    assert isinstance(val, int)
    assert val == 187
    out = tmp_path / "dif_file_size_bytes.ndjson"
    write_ndjson([{"metric": "dif_file_size_bytes", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 187


def test_dif_has_string_cells(tmp_path):
    val = dif_has_string_cells(_DIF)
    assert isinstance(val, bool)
    assert val is True
    out = tmp_path / "dif_has_string_cells.ndjson"
    write_ndjson([{"metric": "dif_has_string_cells", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is True


def test_all_three_formats_batch_ndjson_export(tmp_path):
    records = [
        {"fmt": "csv", "metric": "csv_alpha_field_count", "value": csv_alpha_field_count(_CSV)},
        {"fmt": "csv", "metric": "csv_file_size_bytes", "value": csv_file_size_bytes(_CSV)},
        {"fmt": "tsv", "metric": "tsv_avg_field_length", "value": tsv_avg_field_length(_TSV)},
        {"fmt": "tsv", "metric": "tsv_file_size_bytes", "value": tsv_file_size_bytes(_TSV)},
        {"fmt": "dif", "metric": "dif_avg_numeric_value", "value": dif_avg_numeric_value(_DIF)},
        {"fmt": "dif", "metric": "dif_has_string_cells", "value": dif_has_string_cells(_DIF)},
    ]
    out = tmp_path / "csv_tsv_dif_gaps_batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 6
    parsed = [json.loads(ln) for ln in lines]
    fmts = {r["fmt"] for r in parsed}
    assert {"csv", "tsv", "dif"} == fmts
