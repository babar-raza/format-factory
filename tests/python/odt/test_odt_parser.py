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


class TestOdtMalformedInput:
    """Hardening tests for malformed / adversarial ODT input (R28 Lane F)."""

    def test_empty_file(self, tmp_path):
        """A zero-byte file must fail gracefully."""
        f = tmp_path / "empty.odt"
        f.write_bytes(b"")
        result = parse_odt(str(f))
        assert result["ok"] is False

    def test_empty_file_strict(self, tmp_path):
        import pytest
        f = tmp_path / "empty.odt"
        f.write_bytes(b"")
        with pytest.raises(Exception):
            parse_odt_strict(str(f))

    def test_random_bytes_not_zip(self, tmp_path):
        """Random garbage that is not a ZIP must be rejected."""
        f = tmp_path / "garbage.odt"
        f.write_bytes(b"\xDE\xAD\xBE\xEF" * 64)
        result = parse_odt(str(f))
        assert result["ok"] is False

    def test_valid_zip_wrong_mimetype(self, tmp_path):
        """A valid ZIP but with wrong mimetype must be rejected."""
        import zipfile as zf
        p = tmp_path / "wrong-mime.odt"
        with zf.ZipFile(p, "w") as z:
            z.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            z.writestr("content.xml", "<x/>")
        result = parse_odt(str(p))
        assert result["ok"] is False
        assert "mimetype" in result["error"].lower() or "Invalid" in result["error"]

    def test_zip_missing_content_xml(self, tmp_path):
        """ZIP with correct mimetype but no content.xml must be rejected."""
        import zipfile as zf
        from odt.odt_parser import ODT_MIMETYPE
        p = tmp_path / "no-content.odt"
        with zf.ZipFile(p, "w") as z:
            z.writestr("mimetype", ODT_MIMETYPE)
        import pytest
        with pytest.raises(OdtInvalidContainerError, match="content.xml"):
            parse_odt_strict(str(p))

    def test_zip_missing_mimetype_entry(self, tmp_path):
        """ZIP without a mimetype entry must be rejected."""
        import zipfile as zf
        p = tmp_path / "no-mime.odt"
        with zf.ZipFile(p, "w") as z:
            z.writestr("content.xml", "<x/>")
        import pytest
        with pytest.raises(OdtInvalidContainerError, match="mimetype"):
            parse_odt_strict(str(p))

    def test_truncated_zip_bytes(self, tmp_path):
        """First 20 bytes of a valid ZIP (truncated mid-header)."""
        import zipfile as zf
        from odt.odt_parser import ODT_MIMETYPE
        full = tmp_path / "full.odt"
        with zf.ZipFile(full, "w") as z:
            z.writestr("mimetype", ODT_MIMETYPE)
            z.writestr("content.xml", "<x/>")
        raw = full.read_bytes()
        trunc = tmp_path / "trunc.odt"
        trunc.write_bytes(raw[:20])
        result = parse_odt(str(trunc))
        assert result["ok"] is False

    def test_xml_with_entity_declaration(self, tmp_path):
        """content.xml with a DOCTYPE entity must not expand (XXE safety)."""
        import zipfile as zf
        from odt.odt_parser import ODT_MIMETYPE
        p = tmp_path / "xxe.odt"
        evil_xml = (
            '<?xml version="1.0"?>'
            '<!DOCTYPE foo [<!ENTITY xxe "INJECTED">]>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">'
            '</office:document-content>'
        )
        with zf.ZipFile(p, "w") as z:
            z.writestr("mimetype", ODT_MIMETYPE)
            z.writestr("content.xml", evil_xml)
        result = parse_odt(str(p))
        if result["ok"]:
            assert "INJECTED" not in str(result)
        else:
            assert result["ok"] is False

    def test_content_xml_not_valid_xml(self, tmp_path):
        """content.xml that is not valid XML must fail gracefully."""
        import zipfile as zf
        from odt.odt_parser import ODT_MIMETYPE
        p = tmp_path / "badxml.odt"
        with zf.ZipFile(p, "w") as z:
            z.writestr("mimetype", ODT_MIMETYPE)
            z.writestr("content.xml", "<<<not xml at all>>>")
        result = parse_odt(str(p))
        assert result["ok"] is False

    def test_content_xml_empty_body(self, tmp_path):
        """content.xml with valid structure but no body content."""
        import zipfile as zf
        from odt.odt_parser import ODT_MIMETYPE
        p = tmp_path / "nobody.odt"
        xml = (
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">'
            '</office:document-content>'
        )
        with zf.ZipFile(p, "w") as z:
            z.writestr("mimetype", ODT_MIMETYPE)
            z.writestr("content.xml", xml)
        doc = parse_odt_strict(str(p))
        # Should succeed but with no content
        assert len(doc.paragraphs) == 0
        assert len(doc.elements) == 0


class TestOdtParserDict:
    """Tests for the dict-returning parse_odt."""

    def test_dict_output(self):
        result = parse_odt(SAMPLES / "valid" / "minimal-document.odt")
        assert result["ok"] is True
        assert result["paragraph_count"] >= 1
        assert "paragraphs" in result
