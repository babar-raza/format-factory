"""Tests for dif_string_density and dif_max_cell_length.

Product deepening: DIF analytics — PDC-DIF-STRDENSITY-MAXCELL-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif import write_dif, DifDocument, DifCell, dif_string_density, dif_max_cell_length


def _make_dif(tmp_path, name, cells_rows):
    rows = []
    for row_data in cells_rows:
        rows.append([DifCell(value=v, value_type=t) for v, t in row_data])
    ncols = max(len(r) for r in rows) if rows else 0
    doc = DifDocument(title="test", vectors=ncols, tuples=len(rows), rows=rows)
    p = tmp_path / f"{name}.dif"
    write_dif(doc, str(p))
    return p


class TestDifStringDensity:
    def test_all_string(self, tmp_path):
        p = _make_dif(tmp_path, "allstr", [[("abc", "string"), ("def", "string")]])
        assert dif_string_density(p) == 1.0

    def test_all_number(self, tmp_path):
        p = _make_dif(tmp_path, "allnum", [[("10", "number"), ("20", "number")]])
        assert dif_string_density(p) == 0.0

    def test_mixed(self, tmp_path):
        p = _make_dif(tmp_path, "mixed", [[("abc", "string"), ("10", "number")]])
        assert 0.0 < dif_string_density(p) < 1.0

    def test_returns_float(self, tmp_path):
        p = _make_dif(tmp_path, "ft", [[("x", "string")]])
        assert isinstance(dif_string_density(p), float)

    def test_bounded(self, tmp_path):
        p = _make_dif(tmp_path, "bound", [[("a", "string")]])
        r = dif_string_density(p)
        assert 0.0 <= r <= 1.0


class TestDifMaxCellLength:
    def test_short_cells(self, tmp_path):
        p = _make_dif(tmp_path, "short", [[("ab", "string"), ("c", "string")]])
        assert dif_max_cell_length(p) == 2

    def test_long_cell(self, tmp_path):
        p = _make_dif(tmp_path, "long", [[("hello world", "string"), ("x", "string")]])
        assert dif_max_cell_length(p) == 11

    def test_single_cell(self, tmp_path):
        p = _make_dif(tmp_path, "one", [[("test", "string")]])
        assert dif_max_cell_length(p) == 4

    def test_returns_int(self, tmp_path):
        p = _make_dif(tmp_path, "ft2", [[("z", "string")]])
        assert isinstance(dif_max_cell_length(p), int)

    def test_non_negative(self, tmp_path):
        p = _make_dif(tmp_path, "nn", [[("a", "string")]])
        assert dif_max_cell_length(p) >= 0
