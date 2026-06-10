"""Tests for to_csv() — TSV to CSV conversion.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-TSV-TO-CSV
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import to_csv


class TestToCsv:
    def test_basic_conversion(self):
        data = b"name\tage\nalice\t30\nbob\t25\n"
        csv = to_csv(data)
        assert "name,age" in csv
        assert "alice,30" in csv
        assert "bob,25" in csv

    def test_returns_string(self):
        assert isinstance(to_csv(b"h\nr\n"), str)

    def test_crlf_line_endings(self):
        data = b"a\tb\nv1\tv2\n"
        csv = to_csv(data)
        lines = csv.split("\r\n")
        assert len(lines) >= 2

    def test_quotes_field_with_comma(self):
        data = "col\nvalue,with,commas\n".encode()
        csv = to_csv(data)
        assert '"value,with,commas"' in csv

    def test_quotes_field_with_double_quote(self):
        data = 'col\nsay "hello"\n'.encode()
        csv = to_csv(data)
        assert '"say ""hello"""' in csv

    def test_empty_input(self):
        csv = to_csv(b"")
        assert csv == ""

    def test_header_included(self):
        data = b"name\tval\nalice\t1\n"
        csv = to_csv(data)
        first_line = csv.split("\r\n")[0]
        assert first_line == "name,val"

    def test_no_tab_in_output(self):
        data = b"a\tb\nv1\tv2\n"
        csv = to_csv(data)
        assert "\t" not in csv

    def test_plain_fields_not_quoted(self):
        data = b"name\tage\nalice\t30\n"
        csv = to_csv(data)
        assert '"alice"' not in csv
        assert '"30"' not in csv
