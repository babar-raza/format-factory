"""
R43 Lane 4B: FODT Python deepening tests — authority proof level.

Extends R42 deepening with:
- Table structure access (name, rows, cells)
- List structure access (items, levels)
- Block type enumeration and heading hierarchy
- Neutral model field type contracts
- Strict vs soft parse divergence guard
- parse_errors/warnings field type contracts
- Error handling on invalid input
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SAMPLES = REPO_ROOT / "samples" / "by-format" / "fodt"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from fodt import parse_fodt, parse_fodt_strict, FORMAT_ID, SPEC_VERSION


# ---------------------------------------------------------------------------
# Table structure access
# ---------------------------------------------------------------------------

class TestTableStructure:
    """R43: Table parsing — name, rows, cells accessible."""

    def test_table_basic_has_tables(self):
        result = parse_fodt_strict(str(SAMPLES / "table-basic.fodt"))
        assert len(result.get("tables", [])) >= 1, "table-basic.fodt must have at least 1 table"

    def test_table_has_name(self):
        result = parse_fodt_strict(str(SAMPLES / "table-basic.fodt"))
        for table in result["tables"]:
            assert "name" in table, f"Table missing 'name' key: {table}"

    def test_table_has_rows(self):
        result = parse_fodt_strict(str(SAMPLES / "table-basic.fodt"))
        table = result["tables"][0]
        assert "rows" in table
        assert len(table["rows"]) >= 1

    def test_table_row_has_cells(self):
        result = parse_fodt_strict(str(SAMPLES / "table-basic.fodt"))
        table = result["tables"][0]
        for row in table["rows"]:
            assert "cells" in row, f"Table row missing 'cells': {row}"

    def test_table_cell_has_text(self):
        result = parse_fodt_strict(str(SAMPLES / "table-basic.fodt"))
        table = result["tables"][0]
        all_cells = [c for row in table["rows"] for c in row["cells"]]
        assert any(c.get("text") for c in all_cells), "At least one cell must have text"

    def test_table_cell_values(self):
        result = parse_fodt_strict(str(SAMPLES / "table-basic.fodt"))
        table = result["tables"][0]
        header_row = table["rows"][0]["cells"]
        texts = [c.get("text", "") for c in header_row]
        assert "Name" in texts or "name" in [t.lower() for t in texts], (
            f"Expected 'Name' in header row cells, got: {texts}"
        )


# ---------------------------------------------------------------------------
# List structure access
# ---------------------------------------------------------------------------

class TestListStructure:
    """R43: List parsing — items and levels accessible."""

    def test_list_basic_has_lists(self):
        result = parse_fodt_strict(str(SAMPLES / "list-basic.fodt"))
        assert len(result.get("lists", [])) >= 1, "list-basic.fodt must have at least 1 list"

    def test_list_has_items(self):
        result = parse_fodt_strict(str(SAMPLES / "list-basic.fodt"))
        for lst in result["lists"]:
            assert "items" in lst, f"List missing 'items': {lst}"
            assert len(lst["items"]) >= 1

    def test_list_item_has_text(self):
        result = parse_fodt_strict(str(SAMPLES / "list-basic.fodt"))
        for lst in result["lists"]:
            for item in lst["items"]:
                assert "text" in item, f"List item missing 'text': {item}"

    def test_list_item_has_level(self):
        result = parse_fodt_strict(str(SAMPLES / "list-basic.fodt"))
        for lst in result["lists"]:
            for item in lst["items"]:
                assert "level" in item, f"List item missing 'level': {item}"
                assert isinstance(item["level"], int)

    def test_list_item_text_content(self):
        result = parse_fodt_strict(str(SAMPLES / "list-basic.fodt"))
        all_texts = [item["text"] for lst in result["lists"] for item in lst["items"]]
        assert len(all_texts) >= 3, "list-basic.fodt expected at least 3 list items"


# ---------------------------------------------------------------------------
# Block type enumeration
# ---------------------------------------------------------------------------

class TestBlockTypeEnumeration:
    """R43: Block types must be 'heading' or 'paragraph'."""

    def test_headings_have_heading_level(self):
        result = parse_fodt_strict(str(SAMPLES / "headings-and-paragraphs.fodt"))
        for block in result["blocks"]:
            if block["type"] == "heading":
                assert block["heading_level"] is not None, (
                    f"Heading block missing heading_level: {block}"
                )
                assert isinstance(block["heading_level"], int)

    def test_paragraphs_have_null_heading_level(self):
        result = parse_fodt_strict(str(SAMPLES / "headings-and-paragraphs.fodt"))
        for block in result["blocks"]:
            if block["type"] == "paragraph":
                assert block["heading_level"] is None, (
                    f"Paragraph block should have heading_level=None: {block}"
                )

    def test_block_type_values_are_valid(self):
        result = parse_fodt_strict(str(SAMPLES / "headings-and-paragraphs.fodt"))
        for block in result["blocks"]:
            assert block["type"] in ("heading", "paragraph"), (
                f"Unexpected block type: {block['type']!r}"
            )


# ---------------------------------------------------------------------------
# Field type contracts
# ---------------------------------------------------------------------------

class TestFieldTypeContracts:
    """R43: Neutral model top-level fields must have correct types."""

    def test_blocks_is_list(self):
        result = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        assert isinstance(result["blocks"], list)

    def test_tables_is_list(self):
        result = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        assert isinstance(result["tables"], list)

    def test_lists_is_list(self):
        result = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        assert isinstance(result["lists"], list)

    def test_warnings_is_list(self):
        result = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        assert isinstance(result["warnings"], list)

    def test_parse_errors_is_list(self):
        result = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        assert isinstance(result["parse_errors"], list)

    def test_format_id_is_fodt(self):
        result = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        assert result["format_id"] == "fodt"

    def test_spec_version_is_string(self):
        result = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        assert isinstance(result["spec_version"], str)


# ---------------------------------------------------------------------------
# Strict vs soft divergence guard
# ---------------------------------------------------------------------------

class TestSoftVsStrictDivergence:
    """R43: parse_fodt soft and strict must agree on valid files."""

    def test_same_block_count(self):
        soft = parse_fodt(str(SAMPLES / "headings-and-paragraphs.fodt"))
        strict = parse_fodt_strict(str(SAMPLES / "headings-and-paragraphs.fodt"))
        assert len(soft["blocks"]) == len(strict["blocks"])

    def test_same_format_id(self):
        soft = parse_fodt(str(SAMPLES / "minimal-document.fodt"))
        strict = parse_fodt_strict(str(SAMPLES / "minimal-document.fodt"))
        assert soft["format_id"] == strict["format_id"]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """R43: Invalid input must return/raise appropriate errors."""

    def test_parse_fodt_nonexistent_returns_error(self):
        result = parse_fodt("/nonexistent/doc.fodt")
        has_error = (
            result.get("error")
            or result.get("parse_errors")
            or result.get("warnings")
        )
        assert has_error, (
            "parse_fodt on nonexistent file should report 'error', 'parse_errors', or 'warnings'"
        )

    def test_parse_fodt_strict_nonexistent_raises(self):
        from fodt import FodtError
        with pytest.raises(FodtError):
            parse_fodt_strict("/nonexistent/doc.fodt")
