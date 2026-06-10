"""Tests for count_rows() — TSV row counting.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-TSV-COUNT-ROWS
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import count_rows

_SAMPLE_WITH_HEADER = b"name\tage\ncity\nalice\t30\nbob\t25\n"
_SAMPLE_NO_HEADER = b"a\tb\nc\td\n"
_EMPTY = b""


class TestCountRows:
    def test_basic_count(self):
        data = b"name\tage\nalice\t30\nbob\t25\n"
        assert count_rows(data) == 2

    def test_empty_input_zero(self):
        assert count_rows(b"") == 0

    def test_single_line_no_header_detected(self):
        # With only one row, TSV parser cannot detect header → 1 data row
        assert count_rows(b"name\tage\n") == 1

    def test_single_row(self):
        assert count_rows(b"col1\tcol2\nval1\tval2\n") == 1

    def test_three_rows(self):
        data = b"h\nr1\nr2\nr3\n"
        assert count_rows(data) == 3

    def test_no_trailing_newline(self):
        data = b"h\nr1\nr2"
        assert count_rows(data) == 2

    def test_returns_int(self):
        assert isinstance(count_rows(b"h\nr1\n"), int)
