"""
Tests for DIF filter_rows_by_value() — filter rows in a DIF data model by column value.

Sprint: FORMAT-FACTORY-SELF-HEALING-PRODUCT-DEEPENING-RNEXT
Taskcard: PD-Q-002
Queue item: pdrnext-q-002
Execution method: QUEUE_DISPATCHED_EXECUTION
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import filter_rows_by_value  # noqa: E402


# Sample DIF data model
_SAMPLE_DATA = {
    "data": [
        ["Alice", "Engineering", 95],
        ["Bob", "Marketing", 87],
        ["Carol", "Engineering", 92],
        ["Dave", "Marketing", 78],
    ]
}


def test_filter_rows_returns_list():
    result = filter_rows_by_value(_SAMPLE_DATA, 1, "Engineering")
    assert isinstance(result, list)


def test_filter_rows_matches_single():
    result = filter_rows_by_value(_SAMPLE_DATA, 0, "Bob")
    assert result == [["Bob", "Marketing", 87]]


def test_filter_rows_matches_multiple():
    result = filter_rows_by_value(_SAMPLE_DATA, 1, "Engineering")
    assert len(result) == 2
    assert ["Alice", "Engineering", 95] in result
    assert ["Carol", "Engineering", 92] in result


def test_filter_rows_no_match():
    result = filter_rows_by_value(_SAMPLE_DATA, 1, "Finance")
    assert result == []


def test_filter_rows_numeric_value():
    result = filter_rows_by_value(_SAMPLE_DATA, 2, 87)
    assert result == [["Bob", "Marketing", 87]]


def test_filter_rows_col_out_of_range():
    result = filter_rows_by_value(_SAMPLE_DATA, 99, "anything")
    assert result == []


def test_filter_rows_empty_data():
    result = filter_rows_by_value({"data": []}, 0, "x")
    assert result == []


def test_filter_rows_no_data_key():
    result = filter_rows_by_value({}, 0, "x")
    assert result == []


def test_filter_rows_does_not_mutate_data():
    import copy
    data_copy = copy.deepcopy(_SAMPLE_DATA)
    filter_rows_by_value(_SAMPLE_DATA, 1, "Engineering")
    assert _SAMPLE_DATA == data_copy


def test_filter_rows_importable_from_package():
    from src.python.dif import filter_rows_by_value as fn
    assert callable(fn)


def test_filter_rows_all_rows_match():
    data = {"data": [["A", 1], ["A", 2], ["A", 3]]}
    result = filter_rows_by_value(data, 0, "A")
    assert len(result) == 3
