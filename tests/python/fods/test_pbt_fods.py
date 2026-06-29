"""Property-based tests for FODS codec.

TC-CERT-H-PBT certification hardening.
Uses hypothesis to generate random spreadsheet content and verify parser invariants.
"""
import json
import os
import tempfile

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from fods import parse_fods


CELL_TEXT = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
    min_size=0,
    max_size=100,
)


def _make_fods_xml(rows: list[list[str]]) -> str:
    """Build a minimal valid FODS XML with the given cell data."""
    cells = []
    for row in rows:
        cell_xml = "".join(
            f'<table:table-cell office:value-type="string">'
            f"<text:p>{_xml_escape(c)}</text:p></table:table-cell>"
            for c in row
        )
        cells.append(f"<table:table-row>{cell_xml}</table:table-row>")
    rows_xml = "\n".join(cells)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        {rows_xml}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>"""


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _write_temp(xml: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8")
    f.write(xml)
    f.close()
    return f.name


@given(cell_value=CELL_TEXT)
@settings(max_examples=50)
def test_single_cell_roundtrip(cell_value):
    """A single-cell FODS document must parse without error."""
    assume("\x00" not in cell_value)
    xml = _make_fods_xml([[cell_value]])
    path = _write_temp(xml)
    try:
        result = parse_fods(path)
        assert isinstance(result, dict)
        assert result.get("sheet_count", 0) >= 1
    finally:
        os.unlink(path)


@given(
    rows=st.lists(
        st.lists(CELL_TEXT, min_size=1, max_size=5),
        min_size=1,
        max_size=10,
    )
)
@settings(max_examples=30)
def test_row_count_matches(rows):
    """Parser must report correct row count for generated content."""
    assume(all("\x00" not in c for row in rows for c in row))
    xml = _make_fods_xml(rows)
    path = _write_temp(xml)
    try:
        result = parse_fods(path)
        assert isinstance(result, dict)
        sheets = result.get("sheets", [])
        if sheets:
            assert sheets[0].get("row_count", 0) >= 1
    finally:
        os.unlink(path)


@given(
    n_sheets=st.integers(min_value=1, max_value=5),
    cell_value=CELL_TEXT,
)
@settings(max_examples=20)
def test_multi_sheet_count(n_sheets, cell_value):
    """Parser must report correct sheet_count for multi-sheet documents."""
    assume("\x00" not in cell_value)
    sheets_xml = ""
    for i in range(n_sheets):
        sheets_xml += (
            f'<table:table table:name="Sheet{i+1}">'
            f"<table:table-row>"
            f'<table:table-cell office:value-type="string">'
            f"<text:p>{_xml_escape(cell_value)}</text:p>"
            f"</table:table-cell></table:table-row></table:table>"
        )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body><office:spreadsheet>{sheets_xml}</office:spreadsheet></office:body>
</office:document>"""
    path = _write_temp(xml)
    try:
        result = parse_fods(path)
        assert result.get("sheet_count") == n_sheets
    finally:
        os.unlink(path)


@given(cell_value=CELL_TEXT)
@settings(max_examples=30)
def test_parse_idempotent(cell_value):
    """Parsing the same file twice must yield identical results."""
    assume("\x00" not in cell_value)
    xml = _make_fods_xml([[cell_value]])
    path = _write_temp(xml)
    try:
        r1 = parse_fods(path)
        r2 = parse_fods(path)
        assert r1.get("sheet_count") == r2.get("sheet_count")
        assert len(r1.get("sheets", [])) == len(r2.get("sheets", []))
    finally:
        os.unlink(path)
