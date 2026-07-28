"""Tests for csv_min_field_length and csv_has_duplicates (Sprint 20)."""
import pytest
from src.python.ff_csv import write_csv_to_file, csv_min_field_length, csv_has_duplicates


def _write(rows, path, headers=None):
    write_csv_to_file(rows, path, headers=headers)
    return path


class TestCsvMinFieldLength:
    def test_basic(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["a", "bb", "ccc"]], p, headers=["h1", "h2", "h3"])
        assert csv_min_field_length(p) == 1

    def test_equal_lengths(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["ab", "cd", "ef"]], p, headers=["h1", "h2", "h3"])
        assert csv_min_field_length(p) >= 1

    def test_multirow(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["x", "yy"], ["zzz", "a"]], p, headers=["h1", "h2"])
        assert csv_min_field_length(p) == 1

    def test_return_type(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["abc"]], p, headers=["h"])
        assert isinstance(csv_min_field_length(p), int)

    def test_non_negative(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["a"]], p, headers=["h"])
        assert csv_min_field_length(p) >= 0


class TestCsvHasDuplicates:
    def test_no_duplicates(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["a", "b"], ["c", "d"]], p, headers=["h1", "h2"])
        assert csv_has_duplicates(p) is False

    def test_with_duplicates(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["a", "b"], ["a", "b"]], p, headers=["h1", "h2"])
        assert csv_has_duplicates(p) is True

    def test_single_row(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["x"]], p, headers=["h"])
        assert csv_has_duplicates(p) is False

    def test_return_type(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["a"]], p, headers=["h"])
        assert isinstance(csv_has_duplicates(p), bool)

    def test_all_same(self, tmp_path):
        p = str(tmp_path / "t.csv")
        _write([["x"], ["x"], ["x"]], p, headers=["h"])
        assert csv_has_duplicates(p) is True
