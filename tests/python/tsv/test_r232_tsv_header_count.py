"""Tests for tsv_header_count (Sprint 22)."""
import pytest
from src.python.tsv import write_tsv, tsv_header_count


class TestTsvHeaderCount:
    def test_two_headers(self, tmp_path):
        p = str(tmp_path / "t.tsv")
        write_tsv([["h1", "h2"], ["a", "b"]], p)
        assert tsv_header_count(p) == 2

    def test_single_header(self, tmp_path):
        p = str(tmp_path / "t.tsv")
        write_tsv([["col1"], ["val"]], p)
        assert tsv_header_count(p) == 1

    def test_many_headers(self, tmp_path):
        p = str(tmp_path / "t.tsv")
        write_tsv([["a", "b", "c", "d", "e"], ["1", "2", "3", "4", "5"]], p)
        assert tsv_header_count(p) == 5

    def test_return_type(self, tmp_path):
        p = str(tmp_path / "t.tsv")
        write_tsv([["h"], ["v"]], p)
        assert isinstance(tsv_header_count(p), int)

    def test_non_negative(self, tmp_path):
        p = str(tmp_path / "t.tsv")
        write_tsv([["h"], ["v"]], p)
        assert tsv_header_count(p) >= 0
