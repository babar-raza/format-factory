"""Tests for sylk_string_density and sylk_nonempty_cell_count (Sprint 21)."""
import pytest
from src.python.sylk import sylk_string_density, sylk_nonempty_cell_count


def _write_sylk(tmp_path, lines):
    p = tmp_path / "test.slk"
    content = "\n".join(lines) + "\n"
    p.write_text(content, encoding="ascii")
    return str(p)


class TestSylkStringDensity:
    def test_all_strings(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            'C;X1;Y1;K"hello"',
            'C;X2;Y1;K"world"',
            "E",
        ])
        d = sylk_string_density(path)
        assert d > 0.0

    def test_all_numeric(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            "C;X1;Y1;K42",
            "C;X2;Y1;K99",
            "E",
        ])
        d = sylk_string_density(path)
        assert d == 0.0

    def test_mixed(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            'C;X1;Y1;K"text"',
            "C;X2;Y1;K42",
            "E",
        ])
        d = sylk_string_density(path)
        assert 0.0 < d < 1.0

    def test_return_type(self, tmp_path):
        path = _write_sylk(tmp_path, ["ID;P", "C;X1;Y1;K1", "E"])
        assert isinstance(sylk_string_density(path), float)

    def test_range(self, tmp_path):
        path = _write_sylk(tmp_path, ["ID;P", 'C;X1;Y1;K"a"', "E"])
        d = sylk_string_density(path)
        assert 0.0 <= d <= 1.0


class TestSylkNonemptyCellCount:
    def test_all_filled(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            "C;X1;Y1;K42",
            'C;X2;Y1;K"abc"',
            "E",
        ])
        assert sylk_nonempty_cell_count(path) == 2

    def test_single_cell(self, tmp_path):
        path = _write_sylk(tmp_path, ["ID;P", "C;X1;Y1;K1", "E"])
        assert sylk_nonempty_cell_count(path) == 1

    def test_return_type(self, tmp_path):
        path = _write_sylk(tmp_path, ["ID;P", "C;X1;Y1;K1", "E"])
        assert isinstance(sylk_nonempty_cell_count(path), int)

    def test_non_negative(self, tmp_path):
        path = _write_sylk(tmp_path, ["ID;P", "E"])
        assert sylk_nonempty_cell_count(path) >= 0

    def test_multiple_rows(self, tmp_path):
        path = _write_sylk(tmp_path, [
            "ID;P",
            "C;X1;Y1;K10",
            "C;X1;Y2;K20",
            "C;X1;Y3;K30",
            "E",
        ])
        assert sylk_nonempty_cell_count(path) == 3
