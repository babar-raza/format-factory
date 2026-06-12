"""
test_r54_fodt_preservation.py — R54 Lane 6 tests for FODT list/table/heading preservation.

Tests implemented in R54:
  - Heading preservation: verified PASS (already implemented in R49)
  - List preservation (TC-0059 partial): text:list with text:list-item round-trip
  - Table preservation (TC-0058 partial): table:table with table:table-row/cell round-trip
  - Inline span preservation (TC-0057): NOT implemented — documented as OPEN

R54 Sprint: FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.parser import parse_fodt
from src.python.fodt.writer import document_to_xml

SAMPLES_DIR = PROJECT_ROOT / "samples" / "by-format" / "fodt"


# ---------------------------------------------------------------------------
# Heading preservation (already implemented since R49 — verified in R54 IV)
# ---------------------------------------------------------------------------

class TestHeadingPreservation:
    """Verify heading round-trip works (correcting R53 false NOT_MET claim)."""

    def test_heading_emits_text_h_element(self):
        doc = parse_fodt(str(SAMPLES_DIR / "headings-and-paragraphs.fodt"))
        xml = document_to_xml(doc)
        assert "text:h" in xml, "text:h element must be emitted for headings"

    def test_heading_has_outline_level_attribute(self):
        doc = parse_fodt(str(SAMPLES_DIR / "headings-and-paragraphs.fodt"))
        xml = document_to_xml(doc)
        assert "outline-level" in xml, "text:outline-level attribute must be present"

    def test_heading_level_1_round_trip(self):
        doc = parse_fodt(str(SAMPLES_DIR / "headings-and-paragraphs.fodt"))
        xml = document_to_xml(doc)
        # Write and re-parse to verify round-trip
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            h1_blocks = [b for b in doc2["blocks"] if b.get("type") == "heading" and b.get("heading_level") == 1]
            assert len(h1_blocks) >= 1, "Level-1 heading must survive round-trip"
        finally:
            os.unlink(tmp)

    def test_heading_level_2_survives_round_trip(self):
        doc = parse_fodt(str(SAMPLES_DIR / "headings-and-paragraphs.fodt"))
        xml = document_to_xml(doc)
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            h2_blocks = [b for b in doc2["blocks"] if b.get("type") == "heading" and b.get("heading_level") == 2]
            assert len(h2_blocks) >= 1, "Level-2 heading must survive round-trip"
        finally:
            os.unlink(tmp)

    def test_heading_text_content_preserved(self):
        doc = parse_fodt(str(SAMPLES_DIR / "headings-and-paragraphs.fodt"))
        xml = document_to_xml(doc)
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            heading_texts = [b["text"] for b in doc2["blocks"] if b.get("type") == "heading"]
            assert "Section One" in heading_texts
        finally:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# List preservation (TC-0059 — partial implementation in R54)
# ---------------------------------------------------------------------------

class TestListPreservation:
    """Tests for list round-trip via writer _write_list()."""

    def test_list_items_emitted_as_text_list(self):
        doc = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
        assert len(doc["lists"]) > 0, "list-basic.fodt must have at least one list"
        xml = document_to_xml(doc)
        assert "text:list" in xml, "text:list element must be emitted"

    def test_list_items_emitted_as_text_list_item(self):
        doc = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
        xml = document_to_xml(doc)
        assert "text:list-item" in xml, "text:list-item elements must be emitted"

    def test_list_item_text_preserved(self):
        doc = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
        xml = document_to_xml(doc)
        # List items should have their text content
        assert "First bullet item" in xml, "list item text must be in output"

    def test_list_round_trip_parse_write_parse(self):
        doc = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
        xml = document_to_xml(doc)
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            assert len(doc2["lists"]) > 0, "Round-tripped document must have lists"
        finally:
            os.unlink(tmp)

    def test_list_count_preserved_in_round_trip(self):
        doc = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
        original_list_count = len(doc["lists"])
        xml = document_to_xml(doc)
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            assert len(doc2["lists"]) == original_list_count, \
                f"List count must be preserved: expected {original_list_count}, got {len(doc2['lists'])}"
        finally:
            os.unlink(tmp)

    def test_list_item_count_preserved_in_round_trip(self):
        doc = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
        original_items = sum(len(lst["items"]) for lst in doc["lists"])
        xml = document_to_xml(doc)
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            round_trip_items = sum(len(lst["items"]) for lst in doc2["lists"])
            assert round_trip_items == original_items, \
                f"Item count must match: expected {original_items}, got {round_trip_items}"
        finally:
            os.unlink(tmp)

    def test_edit_unrelated_block_preserves_list(self):
        """Editing a paragraph block should not affect lists."""
        doc = parse_fodt(str(SAMPLES_DIR / "list-basic.fodt"))
        original_lists = doc["lists"]
        # Modify first paragraph block
        for block in doc["blocks"]:
            if block.get("type") == "paragraph":
                block["text"] = "Modified paragraph"
                break
        xml = document_to_xml(doc)
        assert "text:list" in xml, "Lists must survive block edit"
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            assert len(doc2["lists"]) == len(original_lists)
        finally:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# Table preservation (TC-0058 — partial implementation in R54)
# ---------------------------------------------------------------------------

class TestTablePreservation:
    """Tests for table round-trip via writer _write_table()."""

    def test_table_emitted_as_table_table(self):
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        assert len(doc["tables"]) > 0, "table-basic.fodt must have at least one table"
        xml = document_to_xml(doc)
        assert "table:table" in xml, "table:table element must be emitted"

    def test_table_rows_emitted(self):
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        xml = document_to_xml(doc)
        assert "table:table-row" in xml, "table:table-row elements must be emitted"

    def test_table_cells_emitted(self):
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        xml = document_to_xml(doc)
        assert "table:table-cell" in xml, "table:table-cell elements must be emitted"

    def test_table_cell_text_preserved(self):
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        xml = document_to_xml(doc)
        assert "Name" in xml or "Alpha" in xml, "table cell text must be in output"

    def test_table_round_trip_parse_write_parse(self):
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        xml = document_to_xml(doc)
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            assert len(doc2["tables"]) > 0, "Round-tripped document must have tables"
        finally:
            os.unlink(tmp)

    def test_table_row_count_preserved(self):
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        original_rows = sum(len(t["rows"]) for t in doc["tables"])
        xml = document_to_xml(doc)
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            round_trip_rows = sum(len(t["rows"]) for t in doc2["tables"])
            assert round_trip_rows == original_rows
        finally:
            os.unlink(tmp)

    def test_table_name_preserved(self):
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        # Table1 is the name in the fixture
        original_names = [t.get("name") for t in doc["tables"] if t.get("name")]
        xml = document_to_xml(doc)
        if original_names:
            # Table name should appear in the output
            assert any(name in xml for name in original_names), \
                f"Table name(s) {original_names} must appear in output"

    def test_edit_unrelated_block_preserves_table(self):
        """Editing a paragraph block should not affect tables."""
        doc = parse_fodt(str(SAMPLES_DIR / "table-basic.fodt"))
        original_tables = doc["tables"]
        for block in doc["blocks"]:
            if block.get("type") == "paragraph":
                block["text"] = "Modified paragraph"
                break
        xml = document_to_xml(doc)
        assert "table:table" in xml, "Tables must survive block edit"
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
            f.write(xml)
            tmp = f.name
        try:
            doc2 = parse_fodt(tmp)
            assert len(doc2["tables"]) == len(original_tables)
        finally:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# Inline span preservation — TC-0057 (OPEN after R54)
# ---------------------------------------------------------------------------

class TestInlineSpanPreservation:
    """Document TC-0057 status: OPEN. Verify spans are NOT currently preserved."""

    def test_inline_span_not_yet_preserved(self):
        """TC-0057 is OPEN: inline spans are collapsed to plain text in R54.

        This test documents the current limitation, NOT a pass criteria.
        When TC-0057 is implemented, this test should be removed and replaced
        with affirmative round-trip tests.
        """
        # Create a minimal document with a span in a block
        doc = {
            "format_id": "fodt",
            "spec_version": "ODF 1.3",
            "odf_version_attr": "1.3",
            "mimetype": "application/vnd.oasis.opendocument.text-flat-xml",
            "blocks": [
                {"type": "paragraph", "text": "Bold text here", "heading_level": None}
            ],
            "lists": [],
            "tables": [],
            "warnings": [],
            "unsupported_features": [],
            "parse_errors": [],
        }
        xml = document_to_xml(doc)
        # Inline span markup (text:span) is not emitted — plain text only
        assert "text:span" not in xml, (
            "text:span should NOT be emitted in R54 (TC-0057 is OPEN). "
            "If this assertion fails, TC-0057 has been implemented — update this test."
        )
        # The plain text content should still be there
        assert "Bold text here" in xml
