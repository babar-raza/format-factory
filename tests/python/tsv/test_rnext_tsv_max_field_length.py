"""Tests for tsv_max_field_length function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import tsv_max_field_length


def _write_tsv(tmp_path, content):
    p = tmp_path / "test.tsv"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestTsvMaxFieldLength:
    def test_simple_two_columns(self, tmp_path):
        path = _write_tsv(tmp_path, "Name\tAge\nAlice\t30\nBob\t25\n")
        assert tsv_max_field_length(path) == 5  # "Alice"

    def test_long_value_in_data(self, tmp_path):
        path = _write_tsv(tmp_path, "A\tB\nshort\tvery_long_value_here\n")
        assert tsv_max_field_length(path) == 20  # "very_long_value_here"

    def test_header_excluded_from_max(self, tmp_path):
        # tsv_max_field_length only considers data rows, not the header row
        path = _write_tsv(tmp_path, "LongHeaderName\tX\n1\t2\n")
        assert tsv_max_field_length(path) == 1  # data rows have "1" and "2"

    def test_single_cell(self, tmp_path):
        path = _write_tsv(tmp_path, "hello\n")
        assert tsv_max_field_length(path) == 5

    def test_empty_cells(self, tmp_path):
        path = _write_tsv(tmp_path, "A\tB\n\t\n")
        # Header "A" is length 1
        assert tsv_max_field_length(path) == 1

    def test_all_same_length(self, tmp_path):
        path = _write_tsv(tmp_path, "AB\tCD\nEF\tGH\n")
        assert tsv_max_field_length(path) == 2

    def test_unicode_characters(self, tmp_path):
        path = _write_tsv(tmp_path, "Col\nHéllo\n")
        assert tsv_max_field_length(path) == 5  # "Héllo" is 5 chars

    def test_importable_from_package(self):
        from tsv import tsv_max_field_length as fn
        assert callable(fn)
