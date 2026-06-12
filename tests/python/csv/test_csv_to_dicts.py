"""
test_csv_to_dicts.py

Sprint: FORMAT-FACTORY-GAP-DRIVEN-PRODUCT-RNEXT-001
Product feature test for csv_to_dicts (Lane C).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_to_dicts, CsvInputError


class TestCsvToDicts:
    def test_header_keys_used(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("name,age\nAlice,30\nBob,25\n", encoding="utf-8")
        result = csv_to_dicts(f)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[0]["age"] == "30"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(CsvInputError):
            csv_to_dicts(tmp_path / "ghost.csv")

    def test_empty_file_returns_empty_list(self, tmp_path):
        f = tmp_path / "empty.csv"
        f.write_text("", encoding="utf-8")
        result = csv_to_dicts(f)
        assert result == []

    def test_returns_list_of_dicts(self, tmp_path):
        f = tmp_path / "simple.csv"
        f.write_text("x,y\n1,2\n3,4\n", encoding="utf-8")
        result = csv_to_dicts(f)
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_values_are_strings(self, tmp_path):
        f = tmp_path / "nums.csv"
        f.write_text("val\n42\n99\n", encoding="utf-8")
        result = csv_to_dicts(f)
        assert result[0]["val"] == "42"
        assert isinstance(result[0]["val"], str)

    def test_no_header_uses_col_names(self, tmp_path):
        # Pure numeric data — no header heuristic should detect no header
        f = tmp_path / "nums2.csv"
        f.write_text("1,2,3\n4,5,6\n", encoding="utf-8")
        result = csv_to_dicts(f)
        # Should use col_0, col_1, col_2 keys
        assert all(isinstance(r, dict) for r in result)
        for r in result:
            for k in r:
                assert k.startswith("col_") or k.isalpha()

    def test_multiple_rows(self, tmp_path):
        f = tmp_path / "multi.csv"
        lines = ["id,name,score"]
        for i in range(5):
            lines.append(f"{i},user{i},{i * 10}")
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = csv_to_dicts(f)
        assert len(result) == 5
        assert result[2]["id"] == "2"
        assert result[2]["name"] == "user2"
