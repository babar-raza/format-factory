"""Tests for TSV count_distinct_values API — Sprint PACKAGING-BREAKTHROUGH."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from tsv.tsv_parser import (
    count_distinct_values,
    write_tsv,
    TsvError,
)


def _make_tsv(tmp_path: Path, headers: list[str], rows: list[list[str]]) -> Path:
    p = tmp_path / "data.tsv"
    write_tsv(rows, p, headers=headers)
    return p


class TestCountDistinctValues:
    def test_simple_distinct(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["Name", "City"], [["Alice", "NY"], ["Bob", "LA"], ["Carol", "NY"]])
        assert count_distinct_values(p, "City") == 2

    def test_all_duplicates(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["X"], [["a"], ["a"], ["a"]])
        assert count_distinct_values(p, "X") == 1

    def test_all_unique(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["V"], [["x"], ["y"], ["z"]])
        assert count_distinct_values(p, "V") == 3

    def test_empty_cells_excluded(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["A"], [["hello"], [""], ["hello"], [""]])
        assert count_distinct_values(p, "A") == 1

    def test_numeric_strings(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["N"], [["1"], ["2"], ["1"], ["3"]])
        assert count_distinct_values(p, "N") == 3

    def test_single_row(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["K"], [["only"]])
        assert count_distinct_values(p, "K") == 1

    def test_column_not_found(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["A"], [["val"]])
        with pytest.raises(TsvError, match="Column not found"):
            count_distinct_values(p, "Missing")

    def test_multi_column_isolation(self, tmp_path: Path) -> None:
        p = _make_tsv(tmp_path, ["A", "B"], [["x", "1"], ["y", "2"], ["x", "1"]])
        assert count_distinct_values(p, "A") == 2
        assert count_distinct_values(p, "B") == 2
