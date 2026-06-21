"""
Dogfood pipeline: ABW remaining + TSV remaining + PGM remaining -> NDJSON export.
Covers ABW: abw_numeric_char_count, abw_punctuation_ratio, abw_vowel_count
Covers TSV: tsv_avg_row_width, tsv_field_uniqueness_ratio, tsv_longest_row_field_count,
            tsv_max_field_value_length, tsv_numeric_field_count, tsv_total_field_length_sum
Covers PGM: pgm_below_average_count, pgm_border_mean, pgm_bottom_row_mean
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_numeric_char_count, abw_punctuation_ratio, abw_vowel_count
from tsv.tsv_parser import (
    tsv_avg_row_width,
    tsv_field_uniqueness_ratio,
    tsv_longest_row_field_count,
    tsv_max_field_value_length,
    tsv_numeric_field_count,
    tsv_total_field_length_sum,
)
from pgm.pgm_parser import pgm_below_average_count, pgm_border_mean, pgm_bottom_row_mean
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _abw_file():
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _tsv_file():
    files = [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]
    return str(files[0])


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


# --- ABW ---

def test_abw_numeric_char_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_numeric_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_numeric_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_punctuation_ratio_returns_float(tmp_path):
    path = _abw_file()
    result = abw_punctuation_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "abw", "function": "abw_punctuation_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_abw_vowel_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_vowel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_vowel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- TSV ---

def test_tsv_avg_row_width_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_avg_row_width(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_avg_row_width", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_field_uniqueness_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_field_uniqueness_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_field_uniqueness_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_longest_row_field_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_longest_row_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_longest_row_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_max_field_value_length_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_max_field_value_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_max_field_value_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_numeric_field_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_numeric_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_numeric_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_total_field_length_sum_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_total_field_length_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_total_field_length_sum", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- PGM ---

def test_pgm_below_average_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_below_average_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_below_average_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_border_mean_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_border_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_border_mean", "mean": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mean"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_bottom_row_mean_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_bottom_row_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_bottom_row_mean", "mean": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mean"] >= 0
    assert json.dumps(loaded[0]) is not None
