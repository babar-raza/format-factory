"""Tests for ods_has_merged_cells and ods_numeric_density.

Product deepening: ODS analytics — TC-H3-002-ODS / PDC-ODS-MERGED-DENSITY-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ods import (
    parse_ods_strict,
    write_ods,
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    ods_has_merged_cells,
    ods_numeric_density,
)


def _make_ods(tmp_path, name, rows):
    cells = []
    for row_data in rows:
        row_cells = [OdsCell(value=v, value_type="string" if isinstance(v, str) and not v.replace(".", "").isdigit() else "float") for v in row_data]
        cells.append(OdsRow(cells=row_cells))
    sheet = OdsSheet(name="Sheet1", rows=cells)
    doc = OdsDocument(sheets=[sheet])
    p = tmp_path / f"{name}.ods"
    write_ods(doc, str(p))
    return p


class TestOdsHasMergedCells:
    def test_no_merged(self, tmp_path):
        p = _make_ods(tmp_path, "no_merge", [["a", "b"], ["c", "d"]])
        assert ods_has_merged_cells(p) is False

    def test_returns_bool(self, tmp_path):
        p = _make_ods(tmp_path, "bool_type", [["x"]])
        assert isinstance(ods_has_merged_cells(p), bool)

    def test_empty_sheet(self, tmp_path):
        p = _make_ods(tmp_path, "empty", [])
        assert ods_has_merged_cells(p) is False

    def test_invalid_sheet_index(self, tmp_path):
        p = _make_ods(tmp_path, "bad_idx", [["a"]])
        assert ods_has_merged_cells(p, sheet_index=99) is False

    def test_consistent(self, tmp_path):
        p = _make_ods(tmp_path, "consist", [["a", "b"]])
        r1 = ods_has_merged_cells(p)
        r2 = ods_has_merged_cells(p)
        assert r1 == r2


class TestOdsNumericDensity:
    def test_all_string(self, tmp_path):
        p = _make_ods(tmp_path, "allstr", [["hello", "world"]])
        result = ods_numeric_density(p)
        assert isinstance(result, float)

    def test_returns_float(self, tmp_path):
        p = _make_ods(tmp_path, "ft", [["1"]])
        assert isinstance(ods_numeric_density(p), float)

    def test_empty(self, tmp_path):
        p = _make_ods(tmp_path, "emptydn", [])
        result = ods_numeric_density(p)
        assert result == 0.0

    def test_non_negative(self, tmp_path):
        p = _make_ods(tmp_path, "nn", [["x"]])
        assert ods_numeric_density(p) >= 0.0

    def test_invalid_index(self, tmp_path):
        p = _make_ods(tmp_path, "bad_idx2", [["1"]])
        assert ods_numeric_density(p, sheet_index=99) == 0.0
