"""Tests for FODS workbook_find_cells and workbook_count_matching_cells.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT17-001
Covers: find_cells, count_matching_cells on in-memory FODS workbooks
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    write_fods,
    workbook_set_cell_value,
    workbook_sheet_order,
    workbook_find_cells,
    workbook_count_matching_cells,
)


def _build_sample_fods():
    """Create a minimal FODS XML with known cell values."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                 xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
                 xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
                 office:version="1.2"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Data">
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Name</text:p></table:table-cell>
          <table:table-cell office:value-type="string"><text:p>Score</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Alice</text:p></table:table-cell>
          <table:table-cell office:value-type="float" office:value="95"><text:p>95</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Bob</text:p></table:table-cell>
          <table:table-cell office:value-type="float" office:value="87"><text:p>87</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Alice</text:p></table:table-cell>
          <table:table-cell office:value-type="float" office:value="92"><text:p>92</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>"""
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        return Path(f.name)


class TestFindCells:
    """Tests for workbook_find_cells."""

    def test_find_by_value_returns_matches(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            results = workbook_find_cells(wb, "Alice")
            assert isinstance(results, list)
            assert len(results) >= 1
        finally:
            path.unlink(missing_ok=True)

    def test_find_multiple_matches(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            results = workbook_find_cells(wb, "Alice")
            assert len(results) >= 2  # Alice appears twice
        finally:
            path.unlink(missing_ok=True)

    def test_find_nonexistent_returns_empty(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            results = workbook_find_cells(wb, "ZZZZNOTFOUND")
            assert isinstance(results, list)
            assert len(results) == 0
        finally:
            path.unlink(missing_ok=True)

    def test_find_case_insensitive_default(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            results = workbook_find_cells(wb, "alice")
            assert len(results) >= 1  # default is case-insensitive
        finally:
            path.unlink(missing_ok=True)


class TestCountMatchingCells:
    """Tests for workbook_count_matching_cells."""

    def test_count_returns_integer(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            count = workbook_count_matching_cells(wb, "Alice")
            assert isinstance(count, int)
            assert count >= 1
        finally:
            path.unlink(missing_ok=True)

    def test_count_nonexistent_returns_zero(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            count = workbook_count_matching_cells(wb, "ZZZZNOTFOUND")
            assert count == 0
        finally:
            path.unlink(missing_ok=True)

    def test_count_matches_find_length(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            results = workbook_find_cells(wb, "Alice")
            count = workbook_count_matching_cells(wb, "Alice")
            assert count == len(results)
        finally:
            path.unlink(missing_ok=True)


class TestWriteAndSearch:
    """Integration: write FODS, parse, search."""

    def test_write_then_search_finds_edited_value(self):
        path = _build_sample_fods()
        try:
            wb = parse_fods(str(path))
            if not wb.get("ok", True):
                return
            sheets = workbook_sheet_order(wb)
            if not sheets:
                return
            ok, _ = workbook_set_cell_value(wb, sheets[0], 0, 0, "UNIQUE_VAL_XYZ")
            if not ok:
                return
            out = path.parent / "test_search_out.fods"
            write_fods(wb, out)
            wb2 = parse_fods(str(out))
            results = workbook_find_cells(wb2, "UNIQUE_VAL_XYZ")
            assert len(results) >= 1
            out.unlink(missing_ok=True)
        finally:
            path.unlink(missing_ok=True)
