"""
Dogfood pipeline: FODT remaining analytics + CSV remaining analytics → NDJSON export.
Covers FODT: fodt_heading_to_paragraph_ratio, fodt_total_table_cells, fodt_avg_sentence_length,
             fodt_total_char_count, fodt_words_per_paragraph, fodt_is_text_heavy
Covers CSV: csv_field_type_variance, csv_row_length_sum, csv_empty_field_ratio,
            csv_string_cell_count, csv_nonempty_row_count, csv_avg_fields_per_row
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodt.neutral_model import (
    fodt_heading_to_paragraph_ratio,
    fodt_total_table_cells,
    fodt_avg_sentence_length,
    fodt_total_char_count,
    fodt_words_per_paragraph,
    fodt_is_text_heavy,
)
from src.python.csv.csv_parser import (
    csv_field_type_variance,
    csv_row_length_sum,
    csv_empty_field_ratio,
    csv_string_cell_count,
    csv_nonempty_row_count,
    csv_avg_fields_per_row,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _csv_file():
    for f in sorted(_CSV_DIR.glob("*.csv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_CSV_DIR.glob("*.csv")))))


def test_fodt_heading_to_paragraph_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_heading_to_paragraph_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_heading_to_paragraph_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_total_table_cells_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_total_table_cells(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_total_table_cells", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_avg_sentence_length_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_avg_sentence_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_avg_sentence_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_total_char_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_total_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_total_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_words_per_paragraph_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_words_per_paragraph(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_words_per_paragraph", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_is_text_heavy_returns_bool(tmp_path):
    path = _fodt_file()
    result = fodt_is_text_heavy(path)
    assert isinstance(result, bool)

    record = {"format": "fodt", "function": "fodt_is_text_heavy", "is_text_heavy": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_text_heavy"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_field_type_variance_returns_float(tmp_path):
    path = _csv_file()
    result = csv_field_type_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_field_type_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_row_length_sum_returns_int(tmp_path):
    path = _csv_file()
    result = csv_row_length_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_row_length_sum", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_empty_field_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_empty_field_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_empty_field_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_string_cell_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_string_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_string_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_nonempty_row_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_nonempty_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_nonempty_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_avg_fields_per_row_returns_float(tmp_path):
    path = _csv_file()
    result = csv_avg_fields_per_row(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_avg_fields_per_row", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None
