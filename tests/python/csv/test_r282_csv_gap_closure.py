"""Tests closing FOSS gaps: csv_avg_cell_length, csv_avg_numeric_value,
csv_empty_column_count, csv_longest_row_index, csv_total_string_length."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_avg_cell_length,
    csv_avg_numeric_value,
    csv_empty_column_count,
    csv_longest_row_index,
    csv_total_string_length,
)


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,city\nAlice,30,NYC\nBob,25,\nCharlie,40,London\n", encoding="utf-8")
    return p


def test_csv_avg_cell_length_returns_float(csv_file):
    result = csv_avg_cell_length(csv_file)
    assert isinstance(result, (int, float))
    assert result > 0


def test_csv_avg_cell_length_value(csv_file):
    result = csv_avg_cell_length(csv_file)
    # 12 cells: name(4) age(3) city(4) Alice(5) 30(2) NYC(3) Bob(3) 25(2) ""(0) Charlie(7) 40(2) London(6)
    # total chars = 41, 12 cells → avg ~3.4
    assert 2.0 < result < 5.0


def test_csv_avg_numeric_value_returns_float(csv_file):
    result = csv_avg_numeric_value(csv_file)
    assert isinstance(result, (int, float))
    # 30+25+40 = 95, 3 values → avg ~31.67
    assert 25.0 < result < 40.0


def test_csv_empty_column_count(csv_file):
    result = csv_empty_column_count(csv_file)
    assert isinstance(result, int)
    assert result >= 0


def test_csv_empty_column_count_with_empty_col(tmp_path):
    p = tmp_path / "empty_col.csv"
    p.write_text("a,,c\n1,,3\n2,,4\n", encoding="utf-8")
    result = csv_empty_column_count(p)
    assert result >= 1


def test_csv_longest_row_index(csv_file):
    result = csv_longest_row_index(csv_file)
    assert isinstance(result, int)
    assert result >= 0


def test_csv_total_string_length_returns_int(csv_file):
    result = csv_total_string_length(csv_file)
    assert isinstance(result, (int, float))
    assert result > 0


def test_csv_total_string_length_value(csv_file):
    result = csv_total_string_length(csv_file)
    # All string content summed
    assert result > 20
