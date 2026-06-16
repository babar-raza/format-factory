"""Tests for gnumeric_string_density and gnumeric_max_cell_length (Sprint 20)."""
import pytest
from src.python.gnumeric import (
    create_gnumeric, write_gnumeric, set_cell_value,
    gnumeric_string_density, gnumeric_max_cell_length,
)


@pytest.fixture()
def tmp(tmp_path):
    return str(tmp_path / "test.gnumeric")


def _write_cells(cells, path):
    """cells: list of (row, col, value). set_cell_value is immutable."""
    model = create_gnumeric([{"name": "Sheet1"}])
    for r, c, v in cells:
        model = set_cell_value(model, 0, r, c, v)
    write_gnumeric(model, path)
    return path


class TestGnumericStringDensity:
    def test_all_numeric(self, tmp):
        _write_cells([(0, 0, "1"), (0, 1, "2.5")], tmp)
        d = gnumeric_string_density(tmp)
        assert d == 0.0

    def test_all_strings(self, tmp):
        _write_cells([(0, 0, "hello"), (0, 1, "world")], tmp)
        d = gnumeric_string_density(tmp)
        assert d == 1.0

    def test_mixed(self, tmp):
        _write_cells([(0, 0, "hello"), (0, 1, "42")], tmp)
        d = gnumeric_string_density(tmp)
        assert 0.0 < d < 1.0

    def test_return_type(self, tmp):
        _write_cells([(0, 0, "x")], tmp)
        assert isinstance(gnumeric_string_density(tmp), float)

    def test_range_bounds(self, tmp):
        _write_cells([(0, 0, "a"), (0, 1, "1")], tmp)
        d = gnumeric_string_density(tmp)
        assert 0.0 <= d <= 1.0


class TestGnumericMaxCellLength:
    def test_single_cell(self, tmp):
        _write_cells([(0, 0, "hello")], tmp)
        assert gnumeric_max_cell_length(tmp) == 5

    def test_longest_wins(self, tmp):
        _write_cells([(0, 0, "a"), (0, 1, "abcdef")], tmp)
        assert gnumeric_max_cell_length(tmp) == 6

    def test_numeric_string(self, tmp):
        _write_cells([(0, 0, "12345")], tmp)
        assert gnumeric_max_cell_length(tmp) == 5

    def test_return_type(self, tmp):
        _write_cells([(0, 0, "x")], tmp)
        assert isinstance(gnumeric_max_cell_length(tmp), int)

    def test_multiple_rows(self, tmp):
        _write_cells([(0, 0, "ab"), (1, 0, "abcd"), (2, 0, "a")], tmp)
        assert gnumeric_max_cell_length(tmp) == 4
