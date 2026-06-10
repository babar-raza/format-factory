"""Tests for advanced TSV functions added in tsv-advanced-export-dif-dogfood sprint.

Covers: merge_tsv, min_column_tsv, sample_rows, sum_column_tsv, sort_rows,
        drop_column, add_column, rename_column
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest
from src.python.tsv.tsv_parser import (
    merge_tsv,
    min_column_tsv,
    sample_rows,
    sum_column_tsv,
    sort_rows,
    drop_column,
    add_column,
    rename_column,
    TsvError,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DATA_A = b"name\tscore\nAlice\t90\nBob\t80\nCarol\t70\n"
DATA_B = b"name\tscore\nDave\t60\nEve\t85\n"
NUMS = b"item\tqty\tprice\nA\t3\t10.0\nB\t5\t20.0\nC\t2\t15.0\n"


# ---------------------------------------------------------------------------
# merge_tsv tests
# ---------------------------------------------------------------------------

def test_merge_tsv_combines_rows():
    result = merge_tsv(DATA_A, DATA_B)
    assert result["row_count"] == 5 or len(result["rows"]) == 5


def test_merge_tsv_preserves_headers():
    result = merge_tsv(DATA_A, DATA_B)
    assert result["headers"] == ["name", "score"]


def test_merge_tsv_mismatched_headers_raises():
    other = b"name\tvalue\nX\t1\n"
    with pytest.raises(TsvError, match="mismatch"):
        merge_tsv(DATA_A, other)


# ---------------------------------------------------------------------------
# min_column_tsv tests
# ---------------------------------------------------------------------------

def test_min_column_tsv_returns_minimum():
    val = min_column_tsv(NUMS, "price")
    assert val == 10.0


def test_min_column_tsv_qty():
    val = min_column_tsv(NUMS, "qty")
    assert val == 2.0


def test_min_column_tsv_missing_column_raises():
    with pytest.raises(TsvError, match="nonexistent"):
        min_column_tsv(NUMS, "nonexistent")


def test_min_column_tsv_empty_returns_zero():
    data = b"name\tval\nA\tnot_a_number\n"
    val = min_column_tsv(data, "val")
    assert val == 0.0


# ---------------------------------------------------------------------------
# sample_rows tests
# ---------------------------------------------------------------------------

def test_sample_rows_returns_n_rows():
    result = sample_rows(DATA_A, 2)
    assert len(result["rows"]) == 2


def test_sample_rows_preserves_headers():
    result = sample_rows(DATA_A, 1)
    assert result["headers"] == ["name", "score"]


def test_sample_rows_more_than_available():
    result = sample_rows(DATA_A, 100)
    assert len(result["rows"]) == 3


def test_sample_rows_zero():
    result = sample_rows(DATA_A, 0)
    assert len(result["rows"]) == 0


# ---------------------------------------------------------------------------
# sum_column_tsv tests
# ---------------------------------------------------------------------------

def test_sum_column_tsv_sums_numbers():
    val = sum_column_tsv(NUMS, "price")
    assert val == 45.0


def test_sum_column_tsv_qty():
    val = sum_column_tsv(NUMS, "qty")
    assert val == 10.0


def test_sum_column_tsv_missing_column_raises():
    with pytest.raises(TsvError, match="total"):
        sum_column_tsv(NUMS, "total")


def test_sum_column_tsv_skips_non_numeric():
    data = b"val\n10\nhello\n20\n"
    val = sum_column_tsv(data, "val")
    assert val == 30.0


# ---------------------------------------------------------------------------
# sort_rows tests
# ---------------------------------------------------------------------------

def test_sort_rows_ascending():
    result = sort_rows(DATA_A, "score")
    scores = [r[1] for r in result["rows"]]
    assert scores == ["70", "80", "90"]


def test_sort_rows_descending():
    result = sort_rows(DATA_A, "score", reverse=True)
    scores = [r[1] for r in result["rows"]]
    assert scores == ["90", "80", "70"]


def test_sort_rows_by_name():
    result = sort_rows(DATA_A, "name")
    names = [r[0] for r in result["rows"]]
    assert names == sorted(names)


def test_sort_rows_missing_column_raises():
    with pytest.raises(TsvError, match="missing"):
        sort_rows(DATA_A, "missing")


# ---------------------------------------------------------------------------
# drop_column tests
# ---------------------------------------------------------------------------

def test_drop_column_removes_column():
    result = drop_column(DATA_A, "score")
    assert "score" not in result["headers"]


def test_drop_column_preserves_other_columns():
    result = drop_column(NUMS, "price")
    assert "item" in result["headers"]
    assert "qty" in result["headers"]


def test_drop_column_rows_shorter():
    result = drop_column(DATA_A, "score")
    for row in result["rows"]:
        assert len(row) == 1


def test_drop_column_missing_raises():
    with pytest.raises(TsvError, match="nothere"):
        drop_column(DATA_A, "nothere")


# ---------------------------------------------------------------------------
# add_column tests
# ---------------------------------------------------------------------------

def test_add_column_appends_column():
    result = add_column(DATA_A, "rank", ["1", "2", "3"])
    assert "rank" in result["headers"]


def test_add_column_rows_have_new_value():
    result = add_column(DATA_A, "rank", ["1st", "2nd", "3rd"])
    assert result["rows"][0][-1] == "1st"


def test_add_column_wrong_length_raises():
    with pytest.raises(TsvError):
        add_column(DATA_A, "rank", ["1", "2"])  # only 2, need 3


# ---------------------------------------------------------------------------
# rename_column tests
# ---------------------------------------------------------------------------

def test_rename_column_changes_header():
    result = rename_column(DATA_A, "score", "points")
    assert "points" in result["headers"]
    assert "score" not in result["headers"]


def test_rename_column_preserves_other_headers():
    result = rename_column(DATA_A, "score", "points")
    assert "name" in result["headers"]


def test_rename_column_missing_old_name_raises():
    with pytest.raises(TsvError, match="nosuchcol"):
        rename_column(DATA_A, "nosuchcol", "newname")
