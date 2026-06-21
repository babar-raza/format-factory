"""
Dogfood pipeline: ABW remaining + TSV remaining + Gnumeric remaining -> NDJSON export.
Covers ABW: abw_all_words_unique, abw_char_per_paragraph, abw_digit_char_count,
            abw_file_size_bytes, abw_is_empty_document, abw_max_word_count_para,
            abw_min_word_count_para, abw_paragraph_text_variance
Covers TSV: tsv_column_count_avg, tsv_field_length_variance
Covers Gnumeric: gnumeric_column_data_rate, gnumeric_nonempty_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_all_words_unique,
    abw_char_per_paragraph,
    abw_digit_char_count,
    abw_file_size_bytes,
    abw_is_empty_document,
    abw_max_word_count_para,
    abw_min_word_count_para,
    abw_paragraph_text_variance,
)
from tsv.tsv_parser import tsv_column_count_avg, tsv_field_length_variance
from gnumeric.gnumeric_codec import gnumeric_column_data_rate, gnumeric_nonempty_ratio
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _abw_file():
    return str(_ABW_DIR / "two-paragraphs.abw")


def _tsv_file():
    files = [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name and "binary" not in f.name]
    return str(files[0])


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def test_abw_all_words_unique_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_all_words_unique(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_all_words_unique", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_char_per_paragraph_returns_float(tmp_path):
    path = _abw_file()
    result = abw_char_per_paragraph(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_char_per_paragraph", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_digit_char_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_digit_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_digit_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_file_size_bytes_returns_int(tmp_path):
    path = _abw_file()
    result = abw_file_size_bytes(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_is_empty_document_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_is_empty_document(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_is_empty_document", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_max_word_count_para_returns_int(tmp_path):
    path = _abw_file()
    result = abw_max_word_count_para(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_max_word_count_para", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_min_word_count_para_returns_int(tmp_path):
    path = _abw_file()
    result = abw_min_word_count_para(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_min_word_count_para", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_paragraph_text_variance_returns_float(tmp_path):
    path = _abw_file()
    result = abw_paragraph_text_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_paragraph_text_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_column_count_avg_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_column_count_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_column_count_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_field_length_variance_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_field_length_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_field_length_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_column_data_rate_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_column_data_rate(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_column_data_rate", "rate": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["rate"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_nonempty_ratio_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_nonempty_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "gnumeric", "function": "gnumeric_nonempty_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None
