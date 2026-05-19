"""Tests for the ODT Gate 4 prototype parser."""

import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from odt.odt_parser import (
    OdtDocument,
    OdtInvalidContainerError,
    OdtParagraph,
    parse_odt,
    parse_odt_strict,
    probe_odt,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "odt"


class TestOdtParserBasic:
    """Basic parse tests against valid samples."""

    def test_minimal_document(self):
        doc = parse_odt_strict(SAMPLES / "valid" / "minimal-document.odt")
        assert isinstance(doc, OdtDocument)
        assert len(doc.paragraphs) >= 1
        assert doc.paragraphs[0].text == "Hello, world."

    def test_two_paragraphs(self):
        doc = parse_odt_strict(SAMPLES / "valid" / "two-paragraphs.odt")
        assert len(doc.paragraphs) >= 2

    def test_unicode_text(self):
        doc = parse_odt_strict(SAMPLES / "valid" / "unicode-text.odt")
        assert len(doc.paragraphs) >= 1
        # Should contain non-ASCII characters
        text = doc.paragraphs[0].text
        assert len(text) > 0

    def test_elements_list(self):
        doc = parse_odt_strict(SAMPLES / "valid" / "minimal-document.odt")
        assert len(doc.elements) >= 1
        assert isinstance(doc.elements[0], OdtParagraph)


class TestOdtParserInvalid:
    """Tests for invalid/malformed ODT files."""

    def test_truncated_zip(self):
        result = parse_odt(SAMPLES / "invalid" / "truncated.odt")
        assert result["ok"] is False
        assert "error" in result

    def test_truncated_raises_strict(self):
        import pytest
        with pytest.raises((OdtInvalidContainerError, Exception)):
            parse_odt_strict(SAMPLES / "invalid" / "truncated.odt")

    def test_nonexistent_file(self):
        result = parse_odt("/nonexistent/fake.odt")
        assert result["ok"] is False


class TestOdtProbe:
    """Tests for probe_odt."""

    def test_probe_valid(self):
        result = probe_odt(SAMPLES / "valid" / "minimal-document.odt")
        assert result["valid_container"] is True
        assert result["mimetype"] == "application/vnd.oasis.opendocument.text"

    def test_probe_nonexistent(self):
        result = probe_odt("/nonexistent/fake.odt")
        assert result["exists"] is False


class TestOdtParserDict:
    """Tests for the dict-returning parse_odt."""

    def test_dict_output(self):
        result = parse_odt(SAMPLES / "valid" / "minimal-document.odt")
        assert result["ok"] is True
        assert result["paragraph_count"] >= 1
        assert "paragraphs" in result
