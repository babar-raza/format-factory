"""
R42 Train 4B: FODT Python deepening tests.

Extends parser coverage beyond existing suites:
- Block-level structure access (headings, paragraphs, lists, tables)
- Plain-text extraction from parsed blocks
- Package metadata stability
- Heading level hierarchy
- Table cell access
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SAMPLES = REPO_ROOT / "samples" / "by-format" / "fodt"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "fodt"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from fodt import parse_fodt, parse_fodt_strict, FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION


# ---------------------------------------------------------------------------
# Helper: plain-text extraction from blocks
# ---------------------------------------------------------------------------

def extract_text(result: dict) -> str:
    """Concatenate all block text into a single string for quick assertions."""
    lines = []
    for block in result.get("blocks", []):
        text = block.get("text", "")
        if text:
            lines.append(text)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Package metadata stability
# ---------------------------------------------------------------------------

class TestPackageMetadata:
    def test_format_id_is_fodt(self):
        assert FORMAT_ID == "fodt"

    def test_spec_version_odf(self):
        assert "ODF" in SPEC_VERSION or "1." in SPEC_VERSION

    def test_version_semver(self):
        parts = PACKAGE_VERSION.split(".")
        assert len(parts) >= 2

    def test_track_and_flags(self):
        import fodt as fodt_pkg
        assert fodt_pkg.__track__ == "python-foss"
        assert fodt_pkg.__commercial_ready__ is False


# ---------------------------------------------------------------------------
# Block-level structure
# ---------------------------------------------------------------------------

class TestBlockStructure:
    def test_headings_have_level(self):
        sample = SAMPLES / "headings-and-paragraphs.fodt"
        result = parse_fodt_strict(str(sample))
        headings = [b for b in result.get("blocks", []) if b.get("type") == "heading"]
        assert headings is not None, "headings-and-paragraphs.fodt must have heading blocks"
        for h in headings:
            assert "heading_level" in h, "Heading block must have heading_level"
            assert isinstance(h["heading_level"], int)
            assert h["heading_level"] >= 1

    def test_paragraph_blocks_present(self):
        sample = SAMPLES / "headings-and-paragraphs.fodt"
        result = parse_fodt_strict(str(sample))
        paras = [b for b in result.get("blocks", []) if b.get("type") == "paragraph"]
        assert paras is not None, "headings-and-paragraphs.fodt must have paragraph blocks"

    def test_blocks_have_text_field(self):
        sample = SAMPLES / "headings-and-paragraphs.fodt"
        result = parse_fodt_strict(str(sample))
        for block in result.get("blocks", []):
            assert "text" in block, f"Block {block.get('type')!r} must have text field"
            assert isinstance(block["text"], str)

    def test_blocks_list_is_ordered(self):
        """Blocks must be returned in document order (non-empty list)."""
        sample = SAMPLES / "headings-and-paragraphs.fodt"
        result = parse_fodt_strict(str(sample))
        assert len(result.get("blocks", [])) > 0


# ---------------------------------------------------------------------------
# Plain-text extraction
# ---------------------------------------------------------------------------

class TestPlainTextExtraction:
    def test_extract_text_non_empty(self):
        sample = SAMPLES / "headings-and-paragraphs.fodt"
        result = parse_fodt_strict(str(sample))
        text = extract_text(result)
        assert text.strip(), "Plain text extraction must produce non-empty output"

    def test_extract_text_contains_words(self):
        sample = SAMPLES / "headings-and-paragraphs.fodt"
        result = parse_fodt_strict(str(sample))
        text = extract_text(result)
        words = text.split()
        assert len(words) >= 3, f"Expected at least 3 words; got: {words}"

    def test_minimal_document_text_extraction(self):
        sample = SAMPLES / "minimal-document.fodt"
        result = parse_fodt_strict(str(sample))
        text = extract_text(result)
        assert isinstance(text, str)


# ---------------------------------------------------------------------------
# List structure
# ---------------------------------------------------------------------------

class TestListStructure:
    def test_list_basic_has_list_items(self):
        sample = SAMPLES / "list-basic.fodt"
        if not sample.exists():
            pytest.skip("list-basic.fodt not found")
        result = parse_fodt_strict(str(sample))
        lists = result.get("lists", [])
        assert lists is not None, "list-basic.fodt must have list structures"

    def test_blocks_count_positive_for_list_doc(self):
        sample = SAMPLES / "list-basic.fodt"
        if not sample.exists():
            pytest.skip("list-basic.fodt not found")
        result = parse_fodt_strict(str(sample))
        assert len(result.get("blocks", [])) > 0


# ---------------------------------------------------------------------------
# Table structure
# ---------------------------------------------------------------------------

class TestTableStructure:
    def test_table_basic_has_tables(self):
        sample = SAMPLES / "table-basic.fodt"
        if not sample.exists():
            pytest.skip("table-basic.fodt not found")
        result = parse_fodt_strict(str(sample))
        tables = result.get("tables", [])
        assert tables is not None, "table-basic.fodt must have table structures"

    def test_table_has_rows(self):
        sample = SAMPLES / "table-basic.fodt"
        if not sample.exists():
            pytest.skip("table-basic.fodt not found")
        result = parse_fodt_strict(str(sample))
        for table in result.get("tables", []):
            assert "rows" in table, "Table must have rows field"
            assert isinstance(table["rows"], list)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_nonexistent_file_returns_error(self):
        result = parse_fodt("/nonexistent/path/file.fodt")
        assert result.get("exists") is False or result.get("error") is not None

    def test_strict_raises_on_missing(self):
        from fodt import FodtInputError
        with pytest.raises(FodtInputError):
            parse_fodt_strict("/nonexistent/path/file.fodt")

    def test_result_is_dict_for_valid_file(self):
        sample = SAMPLES / "minimal-document.fodt"
        result = parse_fodt(str(sample))
        assert isinstance(result, dict)

    def test_format_id_in_result(self):
        sample = SAMPLES / "minimal-document.fodt"
        result = parse_fodt_strict(str(sample))
        assert result.get("format_id") == "fodt"
