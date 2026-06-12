"""Automated dogfood chain test: ODS parse -> CSV export -> count_distinct_values.

Repairs DOGFOOD-ODS-CSV-001 rework item — replaces manual log with automated pytest.

Sprint: PRODUCT-API-BROADENING-20260612
"""

from __future__ import annotations

import os
import tempfile
import zipfile

import pytest

from src.python.ods.ods_parser import (
    parse_ods_strict,
    ods_to_csv,
    count_distinct_values,
    get_row_count,
    get_sheet_names,
    OdsError,
)


# ---------------------------------------------------------------------------
# Helper: create a minimal ODS file with known data
# ---------------------------------------------------------------------------

NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
MIMETYPE = "application/vnd.oasis.opendocument.spreadsheet"


def _cell(val: str, vtype: str = "string") -> str:
    if vtype == "float":
        return (
            f'<table:table-cell office:value-type="float" office:value="{val}">'
            f"<text:p>{val}</text:p></table:table-cell>"
        )
    return (
        f'<table:table-cell office:value-type="string">'
        f"<text:p>{val}</text:p></table:table-cell>"
    )


def _empty() -> str:
    return "<table:table-cell/>"


def _make_ods(rows: list[list[tuple[str, str]]], sheet_name: str = "Data") -> str:
    """Create ODS from rows of (value, type) tuples. Return path."""
    row_xmls = []
    for row in rows:
        cells = []
        for val, vt in row:
            if val == "":
                cells.append(_empty())
            else:
                cells.append(_cell(val, vt))
        row_xmls.append(f"<table:table-row>{''.join(cells)}</table:table-row>")

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
  xmlns:office="{NS_OFFICE}"
  xmlns:table="{NS_TABLE}"
  xmlns:text="{NS_TEXT}">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="{sheet_name}">
        {''.join(row_xmls)}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document-content>"""

    fd, path = tempfile.mkstemp(suffix=".ods")
    os.close(fd)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", MIMETYPE)
        zf.writestr("content.xml", content)
    return path


# ---------------------------------------------------------------------------
# Test data: a small product catalog
# ---------------------------------------------------------------------------

CATALOG_ROWS = [
    [("Product", "string"), ("Category", "string"), ("Price", "string")],
    [("Widget A", "string"), ("Electronics", "string"), ("29.99", "float")],
    [("Widget B", "string"), ("Electronics", "string"), ("49.99", "float")],
    [("Gadget C", "string"), ("Home", "string"), ("15.00", "float")],
    [("Widget D", "string"), ("Electronics", "string"), ("39.99", "float")],
    [("Gadget E", "string"), ("Home", "string"), ("25.00", "float")],
]


# ---------------------------------------------------------------------------
# Dogfood chain tests
# ---------------------------------------------------------------------------


def test_dogfood_parse_ods_returns_valid_document():
    """Step 1: parse_ods_strict returns OdsDocument with expected structure."""
    path = _make_ods(CATALOG_ROWS, sheet_name="Catalog")
    try:
        doc = parse_ods_strict(path)
        assert doc is not None
        names = get_sheet_names(path)
        assert "Catalog" in names
        rows = get_row_count(path)
        assert rows == 6  # header + 5 data rows
    finally:
        os.unlink(path)


def test_dogfood_ods_to_csv_contains_expected_data():
    """Step 2: ods_to_csv produces CSV string with all rows and headers."""
    path = _make_ods(CATALOG_ROWS, sheet_name="Catalog")
    try:
        csv_str = ods_to_csv(path)
        assert isinstance(csv_str, str)
        lines = [l for l in csv_str.strip().split("\n") if l.strip()]
        assert len(lines) >= 6  # header + 5 data
        assert "Product" in lines[0]
        assert "Category" in lines[0]
        assert "Widget A" in csv_str
        assert "Electronics" in csv_str
        assert "Gadget C" in csv_str
    finally:
        os.unlink(path)


def test_dogfood_count_distinct_on_category_column():
    """Step 3: count_distinct_values returns exact count for Category column."""
    path = _make_ods(CATALOG_ROWS, sheet_name="Catalog")
    try:
        # Column 1 = Category header + Electronics (x3) + Home (x2) = 3 distinct
        distinct = count_distinct_values(path, col=1)
        assert distinct == 3
    finally:
        os.unlink(path)


def test_dogfood_count_distinct_on_product_column():
    """Step 3b: count_distinct_values on Product column — all unique."""
    path = _make_ods(CATALOG_ROWS, sheet_name="Catalog")
    try:
        # Column 0 = Product: header + 5 unique product names = 6 distinct
        distinct = count_distinct_values(path, col=0)
        assert distinct == 6
    finally:
        os.unlink(path)


def test_dogfood_full_chain_parse_csv_distinct():
    """Full chain: create ODS -> parse -> CSV export -> count_distinct -> verify."""
    path = _make_ods(CATALOG_ROWS, sheet_name="Catalog")
    try:
        # Parse
        doc = parse_ods_strict(path)
        assert doc is not None

        # CSV export
        csv_str = ods_to_csv(path)
        assert "Widget A" in csv_str
        assert "Home" in csv_str

        # Count distinct on category (header + Electronics + Home = 3)
        cat_distinct = count_distinct_values(path, col=1)
        assert cat_distinct == 3

        # Count distinct on product
        prod_distinct = count_distinct_values(path, col=0)
        assert prod_distinct == 6

        # Row count
        assert get_row_count(path) == 6
    finally:
        os.unlink(path)
