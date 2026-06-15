"""Tests for sylk_has_header function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import sylk_has_header


def _write_sylk(tmp_path, lines):
    """Write a SYLK file from record lines (ID/C/E records)."""
    p = tmp_path / "test.slk"
    content = "\n".join(lines) + "\n"
    p.write_text(content, encoding="ascii")
    return str(p)


class TestSylkHasHeader:
    def test_header_row_all_strings(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            'C;X1;Y1;K"Name"',
            'C;X2;Y1;K"Age"',
            "C;X1;Y2;K42",
            "E",
        ])
        assert sylk_has_header(path) is True

    def test_no_header_all_numeric(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            "C;X1;Y1;K100",
            "C;X2;Y1;K200",
            "C;X1;Y2;K300",
            "E",
        ])
        assert sylk_has_header(path) is False

    def test_mixed_first_row_not_header(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            'C;X1;Y1;K"Name"',
            "C;X2;Y1;K42",
            "E",
        ])
        assert sylk_has_header(path) is False

    def test_empty_document_no_header(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            "E",
        ])
        assert sylk_has_header(path) is False

    def test_single_string_cell_is_header(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            'C;X1;Y1;K"Header"',
            "E",
        ])
        assert sylk_has_header(path) is True

    def test_data_only_in_row2(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            "C;X1;Y2;K99",
            "E",
        ])
        assert sylk_has_header(path) is False

    def test_three_string_columns_header(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            'C;X1;Y1;K"First"',
            'C;X2;Y1;K"Last"',
            'C;X3;Y1;K"Email"',
            "C;X1;Y2;K42",
            "E",
        ])
        assert sylk_has_header(path) is True

    def test_importable_from_package(self):
        from sylk import sylk_has_header as fn
        assert callable(fn)
