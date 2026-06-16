"""Tests for fods_avg_cells_per_sheet and fods_has_empty_sheets (Sprint 28)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods_strict, fods_avg_cells_per_sheet, fods_has_empty_sheets


_FODS_TMPL = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
{sheets}
    </office:spreadsheet>
  </office:body>
</office:document>
"""

_SHEET_TMPL = """\
      <table:table table:name="{name}">
{rows}
      </table:table>"""

_ROW_CELL = """\
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>{val}</text:p></table:table-cell>
        </table:table-row>"""


def _make_fods(tmp_path, name, sheets_data):
    """sheets_data: list of (sheet_name, list_of_cell_values)."""
    sheet_xmls = []
    for sname, cells in sheets_data:
        rows = "\n".join(_ROW_CELL.format(val=v) for v in cells)
        sheet_xmls.append(_SHEET_TMPL.format(name=sname, rows=rows))
    doc = _FODS_TMPL.format(sheets="\n".join(sheet_xmls))
    p = tmp_path / f"{name}.fods"
    p.write_text(doc, encoding="utf-8")
    return str(p)


def _wb(path):
    return parse_fods_strict(path)


class TestFodsAvgCellsPerSheet:
    def test_return_type(self, tmp_path):
        p = _make_fods(tmp_path, "rt", [("S1", ["a", "b"])])
        assert isinstance(fods_avg_cells_per_sheet(_wb(p)), float)

    def test_two_cells_one_sheet(self, tmp_path):
        p = _make_fods(tmp_path, "tc", [("S1", ["a", "b"])])
        assert fods_avg_cells_per_sheet(_wb(p)) == 2.0

    def test_four_cells_one_sheet(self, tmp_path):
        p = _make_fods(tmp_path, "fc", [("S1", ["a", "b", "c", "d"])])
        assert fods_avg_cells_per_sheet(_wb(p)) == 4.0

    def test_no_sheets_returns_zero(self, tmp_path):
        p = _make_fods(tmp_path, "ns", [])
        assert fods_avg_cells_per_sheet(_wb(p)) == 0.0

    def test_nonnegative(self, tmp_path):
        p = _make_fods(tmp_path, "nn", [("S1", ["x"])])
        assert fods_avg_cells_per_sheet(_wb(p)) >= 0.0


class TestFodsHasEmptySheets:
    def test_return_type(self, tmp_path):
        p = _make_fods(tmp_path, "rt2", [("S1", ["a"])])
        assert isinstance(fods_has_empty_sheets(_wb(p)), bool)

    def test_no_empty_sheets(self, tmp_path):
        p = _make_fods(tmp_path, "ne", [("S1", ["a"]), ("S2", ["b"])])
        assert fods_has_empty_sheets(_wb(p)) is False

    def test_empty_sheet_detected(self, tmp_path):
        p = _make_fods(tmp_path, "es", [("S1", ["a"]), ("S2", [])])
        assert fods_has_empty_sheets(_wb(p)) is True

    def test_all_sheets_empty(self, tmp_path):
        p = _make_fods(tmp_path, "ae", [("S1", []), ("S2", [])])
        assert fods_has_empty_sheets(_wb(p)) is True

    def test_single_nonempty_sheet(self, tmp_path):
        p = _make_fods(tmp_path, "sn", [("S1", ["hello", "world"])])
        assert fods_has_empty_sheets(_wb(p)) is False
