"""
tests/python/tsv/test_r178_tsv_unique_column_values.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT46-001
Tests for unique_column_values() — sorted unique values in a TSV column.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import unique_column_values


def _make_tsv(rows: list[list[str]]) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".tsv", delete=False, mode="w", newline="")
    tmp.write("\t".join(rows[0]) + "\n")
    for row in rows[1:]:
        tmp.write("\t".join(row) + "\n")
    tmp.close()
    return tmp.name


class TestUniqueColumnValues:
    def test_unique_with_duplicates(self):
        path = _make_tsv([["name", "age"], ["Alice", "30"], ["Bob", "25"], ["Alice", "35"]])
        try:
            result = unique_column_values(path, "name")
            assert result == ["Alice", "Bob"]
        finally:
            os.unlink(path)

    def test_unique_ages_sorted(self):
        path = _make_tsv([["name", "age"], ["Alice", "30"], ["Bob", "25"], ["Alice", "35"]])
        try:
            result = unique_column_values(path, "age")
            assert result == ["25", "30", "35"]
        finally:
            os.unlink(path)

    def test_no_duplicates_returns_all(self):
        path = _make_tsv([["x"], ["alpha"], ["beta"], ["gamma"]])
        try:
            result = unique_column_values(path, "x")
            assert result == ["alpha", "beta", "gamma"]
        finally:
            os.unlink(path)

    def test_returns_sorted_list(self):
        path = _make_tsv([["val"], ["z"], ["a"], ["m"]])
        try:
            result = unique_column_values(path, "val")
            assert result == sorted(result)
        finally:
            os.unlink(path)

    def test_returns_list(self):
        path = _make_tsv([["col"], ["x"]])
        try:
            result = unique_column_values(path, "col")
            assert isinstance(result, list)
        finally:
            os.unlink(path)

    def test_exported_from_init(self):
        from src.python.tsv import unique_column_values as fn
        path = _make_tsv([["k"], ["v1"], ["v2"], ["v1"]])
        try:
            result = fn(path, "k")
            assert result == ["v1", "v2"]
        finally:
            os.unlink(path)
