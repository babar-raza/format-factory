"""Tests for tsv_numeric_density and tsv_unique_row_count.

Product deepening: TSV analytics — PDC-TSV-DENSITY-UNIQUE-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv import write_tsv, tsv_numeric_density, tsv_unique_row_count


def _make_tsv(tmp_path, name, rows):
    p = tmp_path / f"{name}.tsv"
    write_tsv(rows, str(p))
    return p


class TestTsvNumericDensity:
    def test_all_numeric(self, tmp_path):
        p = _make_tsv(tmp_path, "allnum", [["1", "2"], ["3", "4"]])
        assert tsv_numeric_density(p) == 1.0

    def test_mixed(self, tmp_path):
        p = _make_tsv(tmp_path, "mixed", [["1", "abc"], ["2", "def"]])
        result = tsv_numeric_density(p)
        assert 0.0 < result < 1.0

    def test_all_string(self, tmp_path):
        p = _make_tsv(tmp_path, "allstr", [["h1", "h2"], ["abc", "def"]])
        assert tsv_numeric_density(p) == 0.0

    def test_returns_float(self, tmp_path):
        p = _make_tsv(tmp_path, "ft", [["h"], ["1"]])
        assert isinstance(tsv_numeric_density(p), float)

    def test_bounded(self, tmp_path):
        p = _make_tsv(tmp_path, "bound", [["h1", "h2"], ["5", "abc"]])
        r = tsv_numeric_density(p)
        assert 0.0 <= r <= 1.0


class TestTsvUniqueRowCount:
    def test_all_unique(self, tmp_path):
        # First row is header, remaining are data rows
        p = _make_tsv(tmp_path, "uniq", [["h1", "h2"], ["a", "b"], ["c", "d"]])
        assert tsv_unique_row_count(p) == 2

    def test_duplicates(self, tmp_path):
        p = _make_tsv(tmp_path, "dups", [["h1", "h2"], ["a", "b"], ["a", "b"], ["c", "d"]])
        assert tsv_unique_row_count(p) == 2

    def test_single_data_row(self, tmp_path):
        p = _make_tsv(tmp_path, "one", [["h1", "h2"], ["x", "y"]])
        assert tsv_unique_row_count(p) == 1

    def test_returns_int(self, tmp_path):
        p = _make_tsv(tmp_path, "ft2", [["h"], ["a"]])
        assert isinstance(tsv_unique_row_count(p), int)

    def test_non_negative(self, tmp_path):
        p = _make_tsv(tmp_path, "nn", [["h"], ["z"]])
        assert tsv_unique_row_count(p) >= 0
