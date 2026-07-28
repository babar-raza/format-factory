"""
tests/python/csv/test_r202_csv_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT12-001
TASK-001 (part A): CSV advanced operations.

Covers: parse_csv, parse_csv_strict, probe_csv, get_row_count, get_column_names,
get_cell_value, csv_column_count, csv_has_header, csv_numeric_row_count,
count_distinct_values, table_stats, column_value_counts, csv_row_length_distribution,
csv_field_type_summary, csv_empty_row_count, csv_max_field_length,
write_csv, write_csv_to_file, get_capabilities.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (
    parse_csv, parse_csv_strict, probe_csv, get_capabilities,
    get_row_count, get_column_names, get_cell_value,
    csv_column_count, csv_has_header, csv_numeric_row_count,
    count_distinct_values,
)
from src.python.ff_csv.csv_writer import write_csv, write_csv_to_file
from src.python.ff_csv.csv_stats import (
    table_stats, column_value_counts, csv_row_length_distribution,
    csv_field_type_summary, csv_empty_row_count, csv_max_field_length,
)

_SAMPLE_CSV = "Name,Score,Grade\nAlice,90,A\nBob,75,B\nCarol,85,A-\n"
_SAMPLE_NUMERIC = "X,Y,Z\n1,2,3\n4,5,6\n7,8,9\n"


def _write_csv_file(content: str = _SAMPLE_CSV) -> str:
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    Path(path).write_text(content, encoding="utf-8")
    return path


class TestCsvParseAndProbe:
    """parse_csv, parse_csv_strict, probe_csv, get_capabilities."""

    def test_parse_csv_returns_dict(self):
        path = _write_csv_file()
        try:
            result = parse_csv(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_parse_csv_has_rows(self):
        path = _write_csv_file()
        try:
            result = parse_csv(path)
            assert "rows" in result or "row_count" in result
        finally:
            os.unlink(path)

    def test_parse_csv_row_count(self):
        path = _write_csv_file()
        try:
            result = parse_csv(path)
            assert result.get("row_count") == 3
        finally:
            os.unlink(path)

    def test_parse_csv_has_header(self):
        path = _write_csv_file()
        try:
            result = parse_csv(path)
            assert result.get("has_header") is True
        finally:
            os.unlink(path)

    def test_parse_csv_strict_returns_dict(self):
        path = _write_csv_file()
        try:
            result = parse_csv_strict(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_probe_csv_true(self):
        path = _write_csv_file()
        try:
            result = probe_csv(path)
            # probe_csv returns a dict with probe info
            assert isinstance(result, dict)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_probe_csv_bad_file_returns_dict(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        Path(path).write_bytes(b"\x00\x01\x02")
        try:
            result = probe_csv(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)


class TestCsvAccessors:
    """get_row_count, get_column_names, get_cell_value, csv_column_count, csv_has_header."""

    def test_get_row_count_three(self):
        path = _write_csv_file()
        try:
            assert get_row_count(path) == 3
        finally:
            os.unlink(path)

    def test_get_column_names_list(self):
        path = _write_csv_file()
        try:
            cols = get_column_names(path)
            assert isinstance(cols, list)
            assert "Name" in cols
        finally:
            os.unlink(path)

    def test_get_cell_value_first(self):
        path = _write_csv_file()
        try:
            val = get_cell_value(path, 0, 0)
            assert val == "Alice"
        finally:
            os.unlink(path)

    def test_get_cell_value_score(self):
        path = _write_csv_file()
        try:
            val = get_cell_value(path, 0, 1)
            assert val == "90" or val == 90
        finally:
            os.unlink(path)

    def test_csv_column_count_three(self):
        path = _write_csv_file()
        try:
            assert csv_column_count(path) == 3
        finally:
            os.unlink(path)

    def test_csv_has_header_true(self):
        path = _write_csv_file()
        try:
            assert csv_has_header(path) is True
        finally:
            os.unlink(path)

    def test_csv_numeric_row_count_int(self):
        path = _write_csv_file()
        try:
            n = csv_numeric_row_count(path)
            assert isinstance(n, int)
        finally:
            os.unlink(path)

    def test_count_distinct_values_int(self):
        path = _write_csv_file()
        try:
            # Column "Grade" has 3 distinct values
            n = count_distinct_values(path, "Grade")
            assert isinstance(n, int)
            assert n == 3
        finally:
            os.unlink(path)


class TestCsvStats:
    """table_stats, column_value_counts, csv_row_length_distribution, csv_field_type_summary, csv_empty_row_count, csv_max_field_length."""

    def test_table_stats_dict(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            stats = table_stats(doc)
            assert isinstance(stats, dict)
            assert stats.get("row_count") == 3
        finally:
            os.unlink(path)

    def test_table_stats_column_count(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            stats = table_stats(doc)
            assert stats.get("column_count") == 3
        finally:
            os.unlink(path)

    def test_column_value_counts_dict(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            # Column index 2 = "Grade"
            counts = column_value_counts(doc, 2)
            assert isinstance(counts, dict)
            assert len(counts) == 3
        finally:
            os.unlink(path)

    def test_csv_row_length_distribution_dict(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            dist = csv_row_length_distribution(doc)
            assert isinstance(dist, dict)
            assert dist.get("is_uniform") is True
        finally:
            os.unlink(path)

    def test_csv_field_type_summary_dict(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            summary = csv_field_type_summary(doc)
            assert isinstance(summary, dict)
        finally:
            os.unlink(path)

    def test_csv_empty_row_count_int(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            n = csv_empty_row_count(doc)
            assert isinstance(n, int)
        finally:
            os.unlink(path)

    def test_csv_max_field_length_int(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            n = csv_max_field_length(doc)
            assert isinstance(n, int)
        finally:
            os.unlink(path)


class TestCsvWrite:
    """write_csv, write_csv_to_file."""

    def test_write_csv_returns_str(self):
        path = _write_csv_file()
        try:
            doc = parse_csv(path)
            csv_str = write_csv(doc)
            assert isinstance(csv_str, str)
            assert len(csv_str) > 0
        finally:
            os.unlink(path)

    def test_write_csv_to_file_creates_file(self):
        path = _write_csv_file()
        fd, out_path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            doc = parse_csv(path)
            write_csv_to_file(doc, out_path)
            assert os.path.getsize(out_path) > 0
        finally:
            os.unlink(path)
            os.unlink(out_path)
