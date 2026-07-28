"""Tests for CSV get_row_count and get_column_names functions (rnext35)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from src.python.ff_csv.csv_parser import get_row_count, get_column_names, CsvError


def _write_csv(content: str) -> str:
    """Write CSV content to a temp file and return path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8")
    tmp.write(content)
    tmp.close()
    return tmp.name


class TestGetRowCount:
    def test_basic_rows(self):
        path = _write_csv("a,b,c\n1,2,3\n4,5,6\n")
        try:
            assert get_row_count(path) == 2
        finally:
            os.unlink(path)

    def test_empty_file(self):
        path = _write_csv("")
        try:
            assert get_row_count(path) == 0
        finally:
            os.unlink(path)

    def test_single_row_no_header(self):
        path = _write_csv("col1,col2,col3\n")
        try:
            # Single row CSV with no subsequent data rows: parser treats it as 1 data row
            assert get_row_count(path) == 1
        finally:
            os.unlink(path)

    def test_single_data_row(self):
        path = _write_csv("name,age\nAlice,30\n")
        try:
            assert get_row_count(path) == 1
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        with pytest.raises(CsvError):
            get_row_count("/nonexistent/path/file.csv")


class TestGetColumnNames:
    def test_basic_headers(self):
        path = _write_csv("name,age,city\nAlice,30,NYC\n")
        try:
            cols = get_column_names(path)
            assert cols == ["name", "age", "city"]
        finally:
            os.unlink(path)

    def test_single_column(self):
        path = _write_csv("value\n1\n2\n")
        try:
            assert get_column_names(path) == ["value"]
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        with pytest.raises(CsvError):
            get_column_names("/nonexistent/path/file.csv")
