"""Tests for CSV count_distinct_values API — Sprint PACKAGING-BREAKTHROUGH."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.csv.csv_parser import (
    count_distinct_values,
    CsvError,
)


def _make_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(content, encoding="utf-8")
    return p


class TestCountDistinctValues:
    def test_simple_distinct(self, tmp_path: Path) -> None:
        p = _make_csv(tmp_path, "Name,City\nAlice,NY\nBob,LA\nCarol,NY\n")
        assert count_distinct_values(p, "City") == 2

    def test_all_duplicates(self, tmp_path: Path) -> None:
        p = _make_csv(tmp_path, "X\na\na\na\n")
        assert count_distinct_values(p, "X") == 1

    def test_all_unique(self, tmp_path: Path) -> None:
        p = _make_csv(tmp_path, "V\nx\ny\nz\n")
        assert count_distinct_values(p, "V") == 3

    def test_empty_cells_excluded(self, tmp_path: Path) -> None:
        p = _make_csv(tmp_path, "A\nhello\n\nhello\n\n")
        assert count_distinct_values(p, "A") == 1

    def test_numeric_strings(self, tmp_path: Path) -> None:
        p = _make_csv(tmp_path, "N\n1\n2\n1\n3\n")
        assert count_distinct_values(p, "N") == 3

    def test_column_not_found_returns_zero(self, tmp_path: Path) -> None:
        p = _make_csv(tmp_path, "A\nval\n")
        assert count_distinct_values(p, "Missing") == 0

    def test_multi_column_isolation(self, tmp_path: Path) -> None:
        p = _make_csv(tmp_path, "A,B\nx,1\ny,2\nx,1\n")
        assert count_distinct_values(p, "A") == 2
        assert count_distinct_values(p, "B") == 2

    def test_invalid_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope.csv"
        with pytest.raises(CsvError):
            count_distinct_values(missing, "A")
