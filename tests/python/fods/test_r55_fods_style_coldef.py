"""
test_r55_fods_style_coldef.py — Tests for TC-0055 (style metadata round-trip)
and TC-0056 (column definitions round-trip) for FODS Python parser+writer.

R55 Train C:
  - TC-0055: office:automatic-styles and office:styles sections are preserved
             on round-trip via the _auto_styles_elem / _styles_elem neutral model fields.
  - TC-0056: table:table-column elements are preserved on round-trip via the
             column_defs list in each sheet dict.

R55 Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.parser import parse_fods_strict
from src.python.fods.writer import workbook_to_xml, write_fods


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}

_STYLE_NS = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"


def _fods_xml(body_parts: str, auto_styles: str = "", styles: str = "") -> str:
    """Build a minimal FODS XML string with optional styles sections."""
    auto_styles_block = (
        f'<office:automatic-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        f' xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"'
        f' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">'
        f'{auto_styles}</office:automatic-styles>'
        if auto_styles else ""
    )
    styles_block = (
        f'<office:styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">'
        f'{styles}</office:styles>'
        if styles else ""
    )
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <office:document
          xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
          xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
          xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
          office:version="1.3"
          office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml">
          {auto_styles_block}
          {styles_block}
          <office:body>
            <office:spreadsheet>
              {body_parts}
            </office:spreadsheet>
          </office:body>
        </office:document>
    """)


def _parse_from_string(xml_str: str, tmp_path: Path) -> dict:
    f = tmp_path / "input.fods"
    f.write_text(xml_str, encoding="utf-8")
    return parse_fods_strict(f)


def _write_and_parse(workbook: dict, tmp_path: Path) -> dict:
    out = tmp_path / "out.fods"
    write_fods(workbook, out)
    return parse_fods_strict(out)


# ===========================================================================
# TC-0055: Style Metadata Preservation
# ===========================================================================

class TestStyleMetadataCapture:
    """Parser captures office:automatic-styles element."""

    def test_auto_styles_captured_in_workbook(self, tmp_path):
        """Parser stores _auto_styles_elem when auto-styles section is present."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
            auto_styles=(
                '<style:style xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
                ' style:name="ce1" style:family="table-cell"/>'
            ),
        )
        wb = _parse_from_string(xml, tmp_path)
        assert "_auto_styles_elem" in wb, "Parser must capture _auto_styles_elem"

    def test_styles_captured_in_workbook(self, tmp_path):
        """Parser stores _styles_elem when styles section is present."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
            styles='<!-- named styles -->',
        )
        wb = _parse_from_string(xml, tmp_path)
        assert "_styles_elem" in wb, "Parser must capture _styles_elem"

    def test_no_styles_section_has_no_elem(self, tmp_path):
        """When no styles section exists, _auto_styles_elem is absent."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
        )
        wb = _parse_from_string(xml, tmp_path)
        assert "_auto_styles_elem" not in wb

    def test_auto_styles_roundtrip_content_preserved(self, tmp_path):
        """After round-trip, the output XML contains the style element name."""
        style_name = "my-bold-style"
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
            auto_styles=(
                f'<style:style xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
                f' style:name="{style_name}" style:family="table-cell"/>'
            ),
        )
        wb = _parse_from_string(xml, tmp_path)
        out_xml = workbook_to_xml(wb)
        assert style_name in out_xml, f"Style name '{style_name}' must appear in round-tripped XML"

    def test_no_styles_workbook_still_serializes(self):
        """A workbook without style elements serializes correctly (no KeyError)."""
        wb = {
            "sheets": [{"name": "Sheet1", "index": 0, "row_count": 0, "rows": []}],
            "odf_version_attr": "1.3",
        }
        xml = workbook_to_xml(wb)
        assert "<office:spreadsheet" in xml


# ===========================================================================
# TC-0056: Column Definitions Preservation
# ===========================================================================

class TestColumnDefsCapture:
    """Parser captures table:table-column elements as column_defs."""

    def test_column_defs_captured_in_sheet(self, tmp_path):
        """Parser stores column_defs list when table:table-column elements exist."""
        col_width_attr = (
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}default-cell-style-name"
        )
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-column table:default-cell-style-name="Default" '
            '  table:style-name="co1"/>'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
        )
        wb = _parse_from_string(xml, tmp_path)
        sheet = wb["sheets"][0]
        assert "column_defs" in sheet, "Sheet must have column_defs when table-column present"
        assert len(sheet["column_defs"]) == 1

    def test_column_def_attributes_preserved(self, tmp_path):
        """Column def dict contains the captured table-column attributes."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-column table:default-cell-style-name="MyStyle"/>'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
        )
        wb = _parse_from_string(xml, tmp_path)
        col_def = wb["sheets"][0]["column_defs"][0]
        # Attribute key is in Clark notation
        style_name_key = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}default-cell-style-name"
        assert style_name_key in col_def
        assert col_def[style_name_key] == "MyStyle"

    def test_no_column_defs_absent_from_sheet(self, tmp_path):
        """When no table:table-column elements exist, column_defs is absent."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
        )
        wb = _parse_from_string(xml, tmp_path)
        sheet = wb["sheets"][0]
        assert "column_defs" not in sheet

    def test_multiple_column_defs_captured(self, tmp_path):
        """Multiple table:table-column elements each produce a column_def entry."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-column table:default-cell-style-name="ColA"/>'
            '<table:table-column table:default-cell-style-name="ColB"/>'
            '<table:table-column table:default-cell-style-name="ColC"/>'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>A</text:p></table:table-cell></table:table-row>'
            '</table:table>',
        )
        wb = _parse_from_string(xml, tmp_path)
        sheet = wb["sheets"][0]
        assert len(sheet["column_defs"]) == 3

    def test_column_defs_roundtrip_in_xml(self, tmp_path):
        """After round-trip, table-column elements appear before rows in the output."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-column table:default-cell-style-name="MyStyle"/>'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>data</text:p></table:table-cell></table:table-row>'
            '</table:table>',
        )
        wb = _parse_from_string(xml, tmp_path)
        out_xml = workbook_to_xml(wb)
        root = ET.fromstring(out_xml)
        cols = root.findall(".//table:table-column", _NS)
        assert cols, "table:table-column elements must appear in round-tripped XML"
        # Style name must be preserved
        assert "MyStyle" in out_xml

    def test_column_defs_appear_before_rows(self, tmp_path):
        """Column def must appear before row data in output (ODF requirement)."""
        xml = _fods_xml(
            '<table:table table:name="Sheet1">'
            '<table:table-column table:default-cell-style-name="X"/>'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>cell</text:p></table:table-cell></table:table-row>'
            '</table:table>',
        )
        wb = _parse_from_string(xml, tmp_path)
        out_xml = workbook_to_xml(wb)
        col_pos = out_xml.find("table-column")
        row_pos = out_xml.find("table-row")
        assert col_pos < row_pos, "Column definitions must precede row data in output"
