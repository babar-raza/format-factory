"""Tests for sylk_numeric_density and sylk_total_cell_count.

Product deepening: SYLK analytics — TC-H3-002-SYLK / PDC-SYLK-DENSITY-TOTAL-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import write_sylk, SylkDocument, SylkCell, sylk_numeric_density, sylk_total_cell_count


def _make_sylk(tmp_path, name, cells):
    doc = SylkDocument(cells=cells)
    p = tmp_path / f"{name}.sylk"
    write_sylk(doc, str(p))
    return p


class TestSylkNumericDensity:
    def test_all_numeric(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="10", value_type="number"),
                 SylkCell(row=0, col=1, value="20", value_type="number")]
        p = _make_sylk(tmp_path, "allnum", cells)
        result = sylk_numeric_density(p)
        assert result > 0

    def test_mixed(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="10", value_type="number"),
                 SylkCell(row=0, col=1, value="abc", value_type="string")]
        p = _make_sylk(tmp_path, "mixed", cells)
        result = sylk_numeric_density(p)
        assert 0.0 < result < 1.0

    def test_all_string(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="abc", value_type="string")]
        p = _make_sylk(tmp_path, "allstr", cells)
        assert sylk_numeric_density(p) == 0.0

    def test_returns_float(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="1", value_type="number")]
        p = _make_sylk(tmp_path, "ft", cells)
        assert isinstance(sylk_numeric_density(p), float)

    def test_bounded(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="5", value_type="number")]
        p = _make_sylk(tmp_path, "bound", cells)
        r = sylk_numeric_density(p)
        assert 0.0 <= r <= 1.0


class TestSylkTotalCellCount:
    def test_two_cells(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="a", value_type="string"),
                 SylkCell(row=0, col=1, value="b", value_type="string")]
        p = _make_sylk(tmp_path, "two", cells)
        assert sylk_total_cell_count(p) == 2

    def test_one_cell(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="x", value_type="string")]
        p = _make_sylk(tmp_path, "one", cells)
        assert sylk_total_cell_count(p) == 1

    def test_returns_int(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="v", value_type="string")]
        p = _make_sylk(tmp_path, "ft2", cells)
        assert isinstance(sylk_total_cell_count(p), int)

    def test_non_negative(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="z", value_type="string")]
        p = _make_sylk(tmp_path, "nn", cells)
        assert sylk_total_cell_count(p) >= 0

    def test_multiple_rows(self, tmp_path):
        cells = [SylkCell(row=0, col=0, value="a", value_type="string"),
                 SylkCell(row=1, col=0, value="b", value_type="string"),
                 SylkCell(row=2, col=0, value="c", value_type="string")]
        p = _make_sylk(tmp_path, "multi", cells)
        assert sylk_total_cell_count(p) == 3
