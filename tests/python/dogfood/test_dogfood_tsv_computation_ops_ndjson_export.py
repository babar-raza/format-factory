"""
Dogfood pipeline: TSV computation ops → NDJSON export.
Covers: sum_column_tsv, min_column_tsv, max_column_tsv, average_column_tsv,
        median_column_tsv, std_column_tsv
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    write_tsv,
    sum_column_tsv,
    min_column_tsv,
    max_column_tsv,
    average_column_tsv,
    median_column_tsv,
    std_column_tsv,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SCORES = [10.0, 20.0, 30.0, 40.0, 50.0]
_EXPECTED_SUM = sum(_SCORES)
_EXPECTED_MIN = min(_SCORES)
_EXPECTED_MAX = max(_SCORES)
_EXPECTED_AVG = sum(_SCORES) / len(_SCORES)


@pytest.fixture
def numeric_tsv(tmp_path):
    rows = [[str(i + 1), str(s)] for i, s in enumerate(_SCORES)]
    dest = tmp_path / "numeric.tsv"
    write_tsv(rows, str(dest), headers=["id", "score"])
    return dest


def test_sum_column_tsv(numeric_tsv, tmp_path):
    total = sum_column_tsv(str(numeric_tsv), "score")
    assert isinstance(total, float)
    assert abs(total - _EXPECTED_SUM) < 1e-6

    record = {"format": "tsv", "function": "sum_column_tsv", "col": "score", "sum": total}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert abs(loaded[0]["sum"] - _EXPECTED_SUM) < 1e-6
    assert json.dumps(loaded[0]) is not None


def test_min_column_tsv(numeric_tsv, tmp_path):
    minimum = min_column_tsv(str(numeric_tsv), "score")
    assert isinstance(minimum, float)
    assert abs(minimum - _EXPECTED_MIN) < 1e-6

    record = {"format": "tsv", "function": "min_column_tsv", "col": "score", "min": minimum}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert abs(loaded[0]["min"] - _EXPECTED_MIN) < 1e-6
    assert json.dumps(loaded[0]) is not None


def test_max_column_tsv(numeric_tsv, tmp_path):
    maximum = max_column_tsv(str(numeric_tsv), "score")
    assert isinstance(maximum, float)
    assert abs(maximum - _EXPECTED_MAX) < 1e-6

    record = {"format": "tsv", "function": "max_column_tsv", "col": "score", "max": maximum}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert abs(loaded[0]["max"] - _EXPECTED_MAX) < 1e-6
    assert loaded[0]["max"] >= loaded[0]["min"] if "min" in loaded[0] else True
    assert json.dumps(loaded[0]) is not None


def test_average_column_tsv(numeric_tsv, tmp_path):
    avg = average_column_tsv(str(numeric_tsv), "score")
    assert isinstance(avg, float)
    assert abs(avg - _EXPECTED_AVG) < 1e-6

    record = {"format": "tsv", "function": "average_column_tsv", "col": "score", "avg": avg}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert abs(loaded[0]["avg"] - _EXPECTED_AVG) < 1e-6
    assert json.dumps(loaded[0]) is not None


def test_median_column_tsv(numeric_tsv, tmp_path):
    med = median_column_tsv(str(numeric_tsv), "score")
    assert isinstance(med, float)
    # Median of [10,20,30,40,50] = 30.0
    assert abs(med - 30.0) < 1e-6

    record = {"format": "tsv", "function": "median_column_tsv", "col": "score", "median": med}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert abs(loaded[0]["median"] - 30.0) < 1e-6
    assert json.dumps(loaded[0]) is not None


def test_std_column_tsv(numeric_tsv, tmp_path):
    std = std_column_tsv(str(numeric_tsv), "score")
    assert isinstance(std, float)
    assert std >= 0.0  # std dev is always non-negative

    record = {"format": "tsv", "function": "std_column_tsv", "col": "score", "std": std}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["std"], float)
    assert loaded[0]["std"] >= 0.0
    assert json.dumps(loaded[0]) is not None
