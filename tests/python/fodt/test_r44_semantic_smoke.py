"""
R44 MT2 Lane 2C: FODT Python semantic smoke tests.

Supersedes R43's insufficient FODT smoke (which reported 'blocks=0 OK').
Verifies the FODT Python package produces real semantic content for all
4 valid samples. These are RC-level contract tests:

- ok is not False (no parse error)
- format_id == 'fodt'
- blocks list is non-empty (NOT just block_count != None)
- Headings are detected in the headings-and-paragraphs sample
- Lists are detected in the list-basic sample
- Tables are detected in the table-basic sample
- Minimal document has a paragraph with text

Sprint: FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
"""

import pathlib
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SAMPLES = REPO_ROOT / "samples" / "by-format" / "fodt"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))
from fodt.parser import parse_fodt  # noqa: E402


def _parse(filename):
    return parse_fodt(str(SAMPLES / filename))


class TestFodtSemanticSmoke:
    """RC-level semantic smoke: every sample must parse with real content."""

    def test_minimal_document_has_paragraph(self):
        r = _parse("minimal-document.fodt")
        assert r.get("error") is None, f"Parse error: {r.get('error')}"
        assert r.get("format_id") == "fodt"
        blocks = r.get("blocks", [])
        assert blocks, "minimal-document.fodt must have at least one block"
        paragraphs = [b for b in blocks if b.get("type") == "paragraph"]
        assert paragraphs, "minimal-document.fodt must have at least one paragraph block"
        assert paragraphs[0].get("text"), "paragraph block must have non-empty text"

    def test_headings_and_paragraphs_has_headings(self):
        """This is the key R43 regression test: blocks must be detected, not just counted."""
        r = _parse("headings-and-paragraphs.fodt")
        assert r.get("error") is None
        blocks = r.get("blocks", [])
        # Must have actual blocks — not the R43 'blocks=0 OK' false pass
        assert len(blocks) >= 3, (
            f"headings-and-paragraphs.fodt must have at least 3 blocks, got {len(blocks)}"
        )
        headings = [b for b in blocks if b.get("type") == "heading"]
        assert headings, "headings-and-paragraphs.fodt must have heading blocks"
        # Headings must have heading_level
        for h in headings:
            assert h.get("heading_level") is not None, (
                f"Heading block must have heading_level: {h}"
            )

    def test_list_basic_has_lists(self):
        r = _parse("list-basic.fodt")
        assert r.get("error") is None
        lists = r.get("lists", [])
        assert lists, "list-basic.fodt must have at least one list"
        for lst in lists:
            items = lst.get("items", [])
            assert items, f"List must have items: {lst}"

    def test_table_basic_has_tables(self):
        r = _parse("table-basic.fodt")
        assert r.get("error") is None
        tables = r.get("tables", [])
        assert tables, "table-basic.fodt must have at least one table"
        for tbl in tables:
            rows = tbl.get("rows", [])
            assert rows, f"Table must have rows: {tbl}"

    def test_all_samples_return_format_id_fodt(self):
        for fodt_file in sorted(SAMPLES.glob("*.fodt")):
            r = parse_fodt(str(fodt_file))
            assert r.get("format_id") == "fodt", (
                f"{fodt_file.name}: expected format_id='fodt', got {r.get('format_id')!r}"
            )

    def test_all_samples_have_nonempty_blocks(self):
        """All valid FODT samples must produce at least one block — R43 regression guard."""
        for fodt_file in sorted(SAMPLES.glob("*.fodt")):
            r = parse_fodt(str(fodt_file))
            if r.get("error"):
                continue
            blocks = r.get("blocks", [])
            assert blocks, (
                f"{fodt_file.name}: blocks list is empty — R43 'blocks=0 OK' regression. "
                "Must detect at least one paragraph or heading."
            )

    def test_all_samples_no_unexpected_parse_errors(self):
        """Valid FODT samples must not return parse_errors."""
        for fodt_file in sorted(SAMPLES.glob("*.fodt")):
            r = parse_fodt(str(fodt_file))
            assert r.get("error") is None, (
                f"{fodt_file.name}: unexpected error: {r.get('error')}"
            )
            errors = r.get("parse_errors", [])
            assert not errors, f"{fodt_file.name}: parse_errors: {errors}"

    def test_headings_sample_heading_text_nonempty(self):
        r = _parse("headings-and-paragraphs.fodt")
        blocks = r.get("blocks", [])
        headings = [b for b in blocks if b.get("type") == "heading"]
        for h in headings:
            assert h.get("text"), f"Heading block must have non-empty text: {h}"
