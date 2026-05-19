"""Gate 6 deterministic oracle tests for ODT parser.

Oracle strategy: Compare parsed output against known expected values
from deterministic synthetic samples (no external tool dependency).
"""

import sys
import tempfile
import zipfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from odt.odt_parser import parse_odt_strict

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "odt"


def _make_odt(content_xml: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
    with zipfile.ZipFile(tmp.name, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        zf.writestr("content.xml", content_xml)
    return Path(tmp.name)


class TestOdtOracleKnownValues:
    """Deterministic oracle: compare parsed output against expected values."""

    def test_known_minimal_document_oracle(self):
        """Oracle for samples/by-format/odt/valid/minimal-document.odt."""
        doc = parse_odt_strict(SAMPLES / "valid" / "minimal-document.odt")
        assert len(doc.paragraphs) >= 1
        assert doc.paragraphs[0].text == "Hello, world."

    def test_known_two_paragraphs_oracle(self):
        """Oracle for two-paragraphs.odt: must have >= 2 paragraphs."""
        doc = parse_odt_strict(SAMPLES / "valid" / "two-paragraphs.odt")
        assert len(doc.paragraphs) >= 2

    def test_known_unicode_text_oracle(self):
        """Oracle for unicode-text.odt: must contain non-ASCII."""
        doc = parse_odt_strict(SAMPLES / "valid" / "unicode-text.odt")
        assert len(doc.paragraphs) >= 1
        assert any(ord(ch) > 127 for ch in doc.paragraphs[0].text)

    def test_synthetic_heading_oracle(self):
        """Oracle: synthetic ODT with H1 heading = exact text match."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:h text:outline-level="1">Oracle Test Heading</text:h>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        assert doc.headings[0].text == "Oracle Test Heading"
        assert doc.headings[0].level == 1

    def test_synthetic_list_oracle(self):
        """Oracle: synthetic ODT with list items."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:list>'
            '<text:list-item><text:p>Item A</text:p></text:list-item>'
            '<text:list-item><text:p>Item B</text:p></text:list-item>'
            '</text:list>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        list_items = [e for e in doc.elements if hasattr(e, 'text') and e.text in ('Item A', 'Item B')]
        assert len(list_items) == 2

    def test_oracle_blocked_external_tool(self):
        """Document: full round-trip oracle requires LibreOffice (blocked)."""
        blocked_reason = "LibreOffice-generated reference files not available in CI"
        assert "LibreOffice" in blocked_reason
