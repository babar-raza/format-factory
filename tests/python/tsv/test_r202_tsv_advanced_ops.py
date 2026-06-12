"""
tests/python/tsv/test_r202_tsv_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT14-001
TASK-001 (part A): TSV advanced operations.

Covers: parse_tsv, parse_tsv_strict, probe_tsv, get_capabilities, load_tsv,
get_headers, get_column, count_rows, column_count, tsv_row_count,
sum_column_tsv, average_column_tsv, get_row, filter_rows, count_distinct_values,
tsv_nonempty_cell_count, tsv_numeric_cell_count, tsv_empty_row_count,
tsv_max_cell_length, write_tsv.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    parse_tsv, parse_tsv_strict, probe_tsv, get_capabilities, load_tsv,
    get_headers, get_column, count_rows, column_count, tsv_row_count,
    sum_column_tsv, average_column_tsv, get_row, filter_rows,
    count_distinct_values, tsv_nonempty_cell_count, tsv_numeric_cell_count,
    tsv_empty_row_count, tsv_max_cell_length, write_tsv,
)

_SAMPLE = "Name\tScore\tGrade\nAlice\t90\tA\nBob\t75\tB\nCarol\t85\tA\n"


def _write_tsv(content: str = _SAMPLE) -> str:
    fd, path = tempfile.mkstemp(suffix=".tsv")
    os.close(fd)
    Path(path).write_text(content, encoding="utf-8")
    return path


class TestTsvParseAndProbe:
    """parse_tsv, parse_tsv_strict, probe_tsv, get_capabilities, load_tsv."""

    def test_parse_tsv_returns_dict(self):
        path = _write_tsv()
        try:
            result = parse_tsv(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_parse_tsv_format_key(self):
        path = _write_tsv()
        try:
            result = parse_tsv(path)
            assert result.get("format") == "tsv"
        finally:
            os.unlink(path)

    def test_parse_tsv_row_count(self):
        path = _write_tsv()
        try:
            result = parse_tsv(path)
            assert result.get("row_count") == 3
        finally:
            os.unlink(path)

    def test_parse_tsv_has_header(self):
        path = _write_tsv()
        try:
            result = parse_tsv(path)
            assert result.get("has_header") is True
        finally:
            os.unlink(path)

    def test_parse_tsv_headers_list(self):
        path = _write_tsv()
        try:
            result = parse_tsv(path)
            assert "Name" in result.get("headers", [])
        finally:
            os.unlink(path)

    def test_probe_tsv_dict(self):
        path = _write_tsv()
        try:
            result = probe_tsv(path)
            assert isinstance(result, dict)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_probe_tsv_delimiter(self):
        path = _write_tsv()
        try:
            result = probe_tsv(path)
            assert result.get("delimiter") == "\t"
        finally:
            os.unlink(path)

    def test_load_tsv_dict(self):
        path = _write_tsv()
        try:
            result = load_tsv(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)

    def test_parse_tsv_strict_dict(self):
        path = _write_tsv()
        try:
            result = parse_tsv_strict(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)


class TestTsvAccessors:
    """get_headers, get_column, count_rows, column_count, tsv_row_count, get_row."""

    def test_get_headers_list(self):
        path = _write_tsv()
        try:
            headers = get_headers(path)
            assert isinstance(headers, list)
            assert "Name" in headers
            assert "Score" in headers
        finally:
            os.unlink(path)

    def test_get_column_values(self):
        path = _write_tsv()
        try:
            col = get_column(path, "Score")
            assert isinstance(col, list)
            assert "90" in col
        finally:
            os.unlink(path)

    def test_count_rows_three(self):
        path = _write_tsv()
        try:
            assert count_rows(path) == 3
        finally:
            os.unlink(path)

    def test_column_count_three(self):
        path = _write_tsv()
        try:
            assert column_count(path) == 3
        finally:
            os.unlink(path)

    def test_tsv_row_count_three(self):
        path = _write_tsv()
        try:
            assert tsv_row_count(path) == 3
        finally:
            os.unlink(path)

    def test_get_row_first(self):
        path = _write_tsv()
        try:
            row = get_row(path, 0)
            assert isinstance(row, list)
            assert "Alice" in row
        finally:
            os.unlink(path)


class TestTsvAnalytics:
    """sum_column_tsv, average_column_tsv, count_distinct_values, tsv_nonempty_cell_count."""

    def test_sum_column_float(self):
        path = _write_tsv()
        try:
            s = sum_column_tsv(path, "Score")
            assert s == 250.0
        finally:
            os.unlink(path)

    def test_average_column_float(self):
        path = _write_tsv()
        try:
            avg = average_column_tsv(path, "Score")
            assert isinstance(avg, float)
            assert abs(avg - 83.33) < 0.1
        finally:
            os.unlink(path)

    def test_count_distinct_values_grade(self):
        path = _write_tsv()
        try:
            n = count_distinct_values(path, "Grade")
            assert isinstance(n, int)
            assert n == 2  # A and B
        finally:
            os.unlink(path)

    def test_tsv_nonempty_cell_count(self):
        path = _write_tsv()
        try:
            n = tsv_nonempty_cell_count(path)
            assert isinstance(n, int)
            assert n == 9  # 3 rows x 3 cols
        finally:
            os.unlink(path)

    def test_tsv_numeric_cell_count(self):
        path = _write_tsv()
        try:
            n = tsv_numeric_cell_count(path)
            assert isinstance(n, int)
            assert n >= 3  # Score column has 3 numbers
        finally:
            os.unlink(path)

    def test_tsv_empty_row_count(self):
        path = _write_tsv()
        try:
            n = tsv_empty_row_count(path)
            assert isinstance(n, int)
            assert n == 0
        finally:
            os.unlink(path)

    def test_tsv_max_cell_length(self):
        path = _write_tsv()
        try:
            n = tsv_max_cell_length(path)
            assert isinstance(n, int)
            assert n >= 5  # "Alice" = 5 chars
        finally:
            os.unlink(path)

    def test_write_tsv_creates_file(self):
        path = _write_tsv()
        fd, out = tempfile.mkstemp(suffix=".tsv")
        os.close(fd)
        try:
            doc = parse_tsv(path)
            write_tsv(doc, out)
            assert os.path.getsize(out) > 0
        finally:
            os.unlink(path)
            os.unlink(out)
