"""Tests for csv_max_row_length and csv_field_type_ratio.

Product deepening: CSV analytics — R238.
"""
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_max_row_length, csv_field_type_ratio


def _write_csv(content):
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    Path(path).write_text(content, encoding="utf-8")
    return path


class TestCsvMaxRowLength:
    def test_uniform_rows(self):
        path = _write_csv("a,b,c\n1,2,3\n4,5,6\n")
        try:
            assert csv_max_row_length(path) == 3
        finally:
            os.unlink(path)

    def test_ragged_rows(self):
        path = _write_csv("a,b\n1,2,3,4\n5,6\n")
        try:
            result = csv_max_row_length(path)
            assert result >= 3
        finally:
            os.unlink(path)

    def test_returns_int(self):
        path = _write_csv("x\n1\n2\n")
        try:
            assert isinstance(csv_max_row_length(path), int)
        finally:
            os.unlink(path)


class TestCsvFieldTypeRatio:
    def test_all_numeric(self):
        path = _write_csv("a,b\n1,2\n3,4\n")
        try:
            result = csv_field_type_ratio(path)
            assert result == float("inf")
        finally:
            os.unlink(path)

    def test_mixed(self):
        path = _write_csv("name,age\nAlice,30\nBob,25\n")
        try:
            result = csv_field_type_ratio(path)
            assert isinstance(result, float)
            assert result > 0
        finally:
            os.unlink(path)

    def test_all_string(self):
        path = _write_csv("a,b\nhello,world\nfoo,bar\n")
        try:
            result = csv_field_type_ratio(path)
            assert result == 0.0
        finally:
            os.unlink(path)
