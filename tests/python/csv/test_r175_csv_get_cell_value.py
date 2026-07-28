"""Tests for CSV get_cell_value function (rnext43)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import get_cell_value


def _make_csv(rows: list[list[str]], header: list[str] | None = None) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", newline="")
    if header:
        tmp.write(",".join(header) + "\n")
    for row in rows:
        tmp.write(",".join(str(v) for v in row) + "\n")
    tmp.close()
    return tmp.name


class TestGetCellValue:
    def test_basic_access(self):
        path = _make_csv([["Alice", "30"], ["Bob", "25"]], header=["name", "age"])
        try:
            result = get_cell_value(path, 0, 0)
            assert result == "Alice"
        finally:
            os.unlink(path)

    def test_second_column(self):
        path = _make_csv([["Alice", "30"]], header=["name", "age"])
        try:
            result = get_cell_value(path, 0, 1)
            assert result == "30"
        finally:
            os.unlink(path)

    def test_second_row(self):
        path = _make_csv([["Alice", "30"], ["Bob", "25"]], header=["name", "age"])
        try:
            result = get_cell_value(path, 1, 0)
            assert result == "Bob"
        finally:
            os.unlink(path)

    def test_out_of_range_row_returns_none(self):
        path = _make_csv([["Alice"]], header=["name"])
        try:
            result = get_cell_value(path, 99, 0)
            assert result is None
        finally:
            os.unlink(path)

    def test_out_of_range_col_returns_none(self):
        path = _make_csv([["Alice"]], header=["name"])
        try:
            result = get_cell_value(path, 0, 99)
            assert result is None
        finally:
            os.unlink(path)
