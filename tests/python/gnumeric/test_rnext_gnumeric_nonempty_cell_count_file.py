"""Tests for gnumeric_nonempty_cell_count_file (file-path API)."""
import gzip
import tempfile
import textwrap
from pathlib import Path

import pytest

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_nonempty_cell_count_file


def _make_gnumeric(cells_xml: str, sheet_name: str = "Sheet1") -> Path:
    """Create a minimal .gnumeric file with given cell XML."""
    xml = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <gnm:Workbook xmlns:gnm="http://www.gnumeric.org/v10.dtd">
          <gnm:Sheets>
            <gnm:Sheet>
              <gnm:Name>{sheet_name}</gnm:Name>
              <gnm:Cells>
                {cells_xml}
              </gnm:Cells>
            </gnm:Sheet>
          </gnm:Sheets>
        </gnm:Workbook>
    """).encode("utf-8")
    tmp = tempfile.NamedTemporaryFile(suffix=".gnumeric", delete=False)
    tmp.write(gzip.compress(xml))
    tmp.close()
    return Path(tmp.name)


class TestBasicCounting:
    def test_single_nonempty_cell(self):
        path = _make_gnumeric(
            '<gnm:Cell Row="0" Col="0"><gnm:Value>hello</gnm:Value></gnm:Cell>'
        )
        assert gnumeric_nonempty_cell_count_file(path) == 1

    def test_multiple_nonempty_cells(self):
        cells = (
            '<gnm:Cell Row="0" Col="0"><gnm:Value>a</gnm:Value></gnm:Cell>'
            '<gnm:Cell Row="0" Col="1"><gnm:Value>b</gnm:Value></gnm:Cell>'
            '<gnm:Cell Row="1" Col="0"><gnm:Value>c</gnm:Value></gnm:Cell>'
        )
        path = _make_gnumeric(cells)
        assert gnumeric_nonempty_cell_count_file(path) == 3

    def test_empty_cells_not_counted(self):
        cells = (
            '<gnm:Cell Row="0" Col="0"><gnm:Value>data</gnm:Value></gnm:Cell>'
            '<gnm:Cell Row="0" Col="1"><gnm:Value></gnm:Value></gnm:Cell>'
        )
        path = _make_gnumeric(cells)
        assert gnumeric_nonempty_cell_count_file(path) == 1

    def test_no_cells_returns_zero(self):
        path = _make_gnumeric("")
        assert gnumeric_nonempty_cell_count_file(path) == 0


class TestSheetIndex:
    def test_default_sheet_zero(self):
        path = _make_gnumeric(
            '<gnm:Cell Row="0" Col="0"><gnm:Value>x</gnm:Value></gnm:Cell>'
        )
        assert gnumeric_nonempty_cell_count_file(path, sheet_idx=0) == 1

    def test_invalid_sheet_raises(self):
        from gnumeric.gnumeric_codec import GnumericError
        path = _make_gnumeric(
            '<gnm:Cell Row="0" Col="0"><gnm:Value>x</gnm:Value></gnm:Cell>'
        )
        with pytest.raises(GnumericError):
            gnumeric_nonempty_cell_count_file(path, sheet_idx=5)


class TestNumericValues:
    def test_numeric_cells_counted(self):
        cells = (
            '<gnm:Cell Row="0" Col="0"><gnm:Value>42</gnm:Value></gnm:Cell>'
            '<gnm:Cell Row="1" Col="0"><gnm:Value>3.14</gnm:Value></gnm:Cell>'
        )
        path = _make_gnumeric(cells)
        assert gnumeric_nonempty_cell_count_file(path) == 2

    def test_mixed_values(self):
        cells = (
            '<gnm:Cell Row="0" Col="0"><gnm:Value>text</gnm:Value></gnm:Cell>'
            '<gnm:Cell Row="0" Col="1"><gnm:Value>99</gnm:Value></gnm:Cell>'
            '<gnm:Cell Row="1" Col="0"><gnm:Value></gnm:Value></gnm:Cell>'
        )
        path = _make_gnumeric(cells)
        assert gnumeric_nonempty_cell_count_file(path) == 2


class TestEdgeCases:
    def test_whitespace_only_cell_is_empty(self):
        """Whitespace-only values are stripped to empty by the parser."""
        cells = '<gnm:Cell Row="0" Col="0"><gnm:Value>  </gnm:Value></gnm:Cell>'
        path = _make_gnumeric(cells)
        # Parser strips whitespace, so "  " becomes "" -> empty
        assert gnumeric_nonempty_cell_count_file(path) == 0

    def test_return_type_is_int(self):
        path = _make_gnumeric("")
        result = gnumeric_nonempty_cell_count_file(path)
        assert isinstance(result, int)
