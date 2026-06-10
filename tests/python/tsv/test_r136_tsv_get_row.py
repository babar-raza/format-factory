"""Tests for get_row() — TSV row accessor by index.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-TSV-GET-ROW
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import get_row

_SAMPLE = b"name\tage\tcity\nAlice\t30\tNY\nBob\t25\tLA\n"


class TestGetRow:
    def test_first_row(self):
        row = get_row(_SAMPLE, 0)
        assert row == ["Alice", "30", "NY"]

    def test_second_row(self):
        row = get_row(_SAMPLE, 1)
        assert row == ["Bob", "25", "LA"]

    def test_returns_list(self):
        row = get_row(_SAMPLE, 0)
        assert isinstance(row, list)

    def test_index_error_out_of_range(self):
        with pytest.raises(IndexError):
            get_row(_SAMPLE, 99)

    def test_index_error_negative(self):
        with pytest.raises(IndexError):
            get_row(_SAMPLE, -1)

    def test_single_data_row(self):
        data = b"col1\tcol2\nval1\tval2\n"
        row = get_row(data, 0)
        assert row == ["val1", "val2"]

    def test_file_source(self, tmp_path):
        f = tmp_path / "data.tsv"
        f.write_text("h1\th2\na\tb\nc\td\n", encoding="utf-8")
        row = get_row(f, 1)
        assert row == ["c", "d"]

    def test_no_header_row(self):
        data = b"single\trow\n"
        row = get_row(data, 0)
        assert row == ["single", "row"]

    def test_three_columns(self):
        data = b"a\tb\tc\n1\t2\t3\n4\t5\t6\n"
        assert get_row(data, 0) == ["1", "2", "3"]
        assert get_row(data, 1) == ["4", "5", "6"]
