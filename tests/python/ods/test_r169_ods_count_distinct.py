"""Tests for ODS count_distinct_values API.

Sprint: PRODUCT-DEEPENING-HEALING-20260612
Skill: /add-python-api
Format: ODS
API: count_distinct_values
"""

from __future__ import annotations

import os
import tempfile
import zipfile
import pytest

from src.python.ods.ods_parser import (
    count_distinct_values,
    OdsError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"

MIMETYPE = "application/vnd.oasis.opendocument.spreadsheet"


def _cell_xml(value: str, value_type: str = "string") -> str:
    if value_type == "float":
        return (
            f'<table:table-cell office:value-type="float" office:value="{value}">'
            f"<text:p>{value}</text:p></table:table-cell>"
        )
    return (
        f'<table:table-cell office:value-type="string">'
        f"<text:p>{value}</text:p></table:table-cell>"
    )


def _empty_cell_xml() -> str:
    return "<table:table-cell/>"


def _make_ods(rows: list[list[str]], value_types: list[list[str]] | None = None) -> str:
    """Create a minimal ODS file and return its path."""
    row_xmls = []
    for r_idx, row in enumerate(rows):
        cells = []
        for c_idx, val in enumerate(row):
            if val == "":
                cells.append(_empty_cell_xml())
            else:
                vt = "string"
                if value_types and r_idx < len(value_types) and c_idx < len(value_types[r_idx]):
                    vt = value_types[r_idx][c_idx]
                cells.append(_cell_xml(val, vt))
        row_xmls.append(f"<table:table-row>{''.join(cells)}</table:table-row>")

    content_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
  xmlns:office="{NS_OFFICE}"
  xmlns:table="{NS_TABLE}"
  xmlns:text="{NS_TEXT}">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        {''.join(row_xmls)}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document-content>"""

    fd, path = tempfile.mkstemp(suffix=".ods")
    os.close(fd)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", MIMETYPE)
        zf.writestr("content.xml", content_xml)
    return path


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------


def test_count_distinct_simple():
    """Three distinct string values in column 0."""
    path = _make_ods([["apple"], ["banana"], ["cherry"]])
    try:
        assert count_distinct_values(path, col=0) == 3
    finally:
        os.unlink(path)


def test_count_distinct_with_duplicates():
    """Column has duplicates — should return unique count only."""
    path = _make_ods([["a"], ["b"], ["a"], ["c"], ["b"]])
    try:
        assert count_distinct_values(path, col=0) == 3
    finally:
        os.unlink(path)


def test_count_distinct_numeric():
    """Distinct numeric float values."""
    path = _make_ods(
        [["10"], ["20"], ["10"], ["30"]],
        value_types=[["float"], ["float"], ["float"], ["float"]],
    )
    try:
        result = count_distinct_values(path, col=0)
        assert result == 3
    finally:
        os.unlink(path)


def test_count_distinct_mixed_types():
    """Mixed string and float values — all distinct."""
    path = _make_ods(
        [["hello"], ["10"], ["world"]],
        value_types=[["string"], ["float"], ["string"]],
    )
    try:
        result = count_distinct_values(path, col=0)
        assert result == 3
    finally:
        os.unlink(path)


def test_count_distinct_multi_column():
    """Verify column isolation — distinct count only for requested column."""
    path = _make_ods([
        ["a", "x"],
        ["b", "x"],
        ["a", "y"],
    ])
    try:
        assert count_distinct_values(path, col=0) == 2
        assert count_distinct_values(path, col=1) == 2
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------


def test_count_distinct_with_empty_cells():
    """Empty cells should be excluded from count."""
    path = _make_ods([["a"], [""], ["b"], [""], ["a"]])
    try:
        assert count_distinct_values(path, col=0) == 2
    finally:
        os.unlink(path)


def test_count_distinct_all_same():
    """All cells have the same value — should return 1."""
    path = _make_ods([["x"], ["x"], ["x"]])
    try:
        assert count_distinct_values(path, col=0) == 1
    finally:
        os.unlink(path)


def test_count_distinct_all_empty():
    """All cells empty — should return 0."""
    path = _make_ods([[""], [""], [""]])
    try:
        assert count_distinct_values(path, col=0) == 0
    finally:
        os.unlink(path)


def test_count_distinct_single_row():
    """Single row with one value."""
    path = _make_ods([["only"]])
    try:
        assert count_distinct_values(path, col=0) == 1
    finally:
        os.unlink(path)


def test_count_distinct_out_of_range_sheet():
    """Invalid sheet index returns 0 (via empty column values)."""
    path = _make_ods([["a"], ["b"]])
    try:
        assert count_distinct_values(path, col=0, sheet_index=99) == 0
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------


def test_count_distinct_invalid_file():
    """Non-ODS file raises OdsError."""
    fd, path = tempfile.mkstemp(suffix=".ods")
    os.write(fd, b"not a zip file")
    os.close(fd)
    try:
        with pytest.raises(OdsError):
            count_distinct_values(path, col=0)
    finally:
        os.unlink(path)
