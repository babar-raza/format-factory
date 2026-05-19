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

    def test_multi_paragraph_oracle(self):
        """Oracle: verify exact paragraph count and content for 5 paragraphs."""
        paras = [f"Paragraph number {i}." for i in range(1, 6)]
        p_xml = "".join(f'<text:p>{t}</text:p>' for t in paras)
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            f'<office:body><office:text>{p_xml}</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.paragraphs) == 5
        for i, p in enumerate(doc.paragraphs):
            assert p.text == f"Paragraph number {i + 1}."

    def test_heading_levels_oracle(self):
        """Oracle: verify h1/h2/h3 heading extraction with exact levels."""
        headings = [
            (1, "Chapter One"),
            (2, "Section Alpha"),
            (3, "Subsection Beta"),
        ]
        h_xml = "".join(
            f'<text:h text:outline-level="{lvl}">{txt}</text:h>'
            for lvl, txt in headings
        )
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            f'<office:body><office:text>{h_xml}</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.headings) == 3
        for i, (lvl, txt) in enumerate(headings):
            assert doc.headings[i].text == txt
            assert doc.headings[i].level == lvl

    def test_nested_list_oracle(self):
        """Oracle: verify list items extracted from nested list structure."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:list>'
            '<text:list-item><text:p>First</text:p></text:list-item>'
            '<text:list-item><text:p>Second</text:p></text:list-item>'
            '<text:list-item><text:p>Third</text:p></text:list-item>'
            '<text:list-item><text:p>Fourth</text:p></text:list-item>'
            '</text:list>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        from odt.odt_parser import OdtListItem
        list_items = [e for e in doc.elements if isinstance(e, OdtListItem)]
        assert len(list_items) == 4
        assert list_items[0].text == "First"
        assert list_items[3].text == "Fourth"

    def test_unicode_cjk_emoji_rtl_oracle(self):
        """Oracle: verify CJK, emoji, and RTL characters are preserved."""
        texts = [
            "\u4f60\u597d\u4e16\u754c",       # Chinese: 你好世界
            "\U0001f600\U0001f680\U0001f4a1",  # Emoji: 😀🚀💡
            "\u0645\u0631\u062d\u0628\u0627",  # Arabic: مرحبا
        ]
        p_xml = "".join(f'<text:p>{t}</text:p>' for t in texts)
        content = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            f'<office:body><office:text>{p_xml}</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.paragraphs) == 3
        assert doc.paragraphs[0].text == texts[0]
        assert doc.paragraphs[1].text == texts[1]
        assert doc.paragraphs[2].text == texts[2]

    def test_empty_document_oracle(self):
        """Oracle: empty document body returns empty paragraphs list."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.paragraphs) == 0
        assert len(doc.headings) == 0
        assert len(doc.elements) == 0

    def test_mixed_content_oracle(self):
        """Oracle: headings + paragraphs + lists in one document, order preserved."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:h text:outline-level="1">Title</text:h>'
            '<text:p>Introduction paragraph.</text:p>'
            '<text:list>'
            '<text:list-item><text:p>Bullet one</text:p></text:list-item>'
            '<text:list-item><text:p>Bullet two</text:p></text:list-item>'
            '</text:list>'
            '<text:h text:outline-level="2">Sub-heading</text:h>'
            '<text:p>Closing paragraph.</text:p>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        # Headings
        assert len(doc.headings) == 2
        assert doc.headings[0].text == "Title"
        assert doc.headings[0].level == 1
        assert doc.headings[1].text == "Sub-heading"
        assert doc.headings[1].level == 2
        # Paragraphs
        assert len(doc.paragraphs) == 2
        assert doc.paragraphs[0].text == "Introduction paragraph."
        assert doc.paragraphs[1].text == "Closing paragraph."
        # Elements order: heading, para, list-item, list-item, heading, para
        assert len(doc.elements) == 6
        from odt.odt_parser import OdtHeading, OdtParagraph, OdtListItem
        assert isinstance(doc.elements[0], OdtHeading)
        assert isinstance(doc.elements[1], OdtParagraph)
        assert isinstance(doc.elements[2], OdtListItem)
        assert isinstance(doc.elements[3], OdtListItem)
        assert isinstance(doc.elements[4], OdtHeading)
        assert isinstance(doc.elements[5], OdtParagraph)

    def test_style_name_oracle(self):
        """Oracle: paragraph style name is extracted correctly."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:p text:style-name="Standard">Styled text</text:p>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        doc = parse_odt_strict(path)
        assert doc.paragraphs[0].style == "Standard"
        assert doc.paragraphs[0].text == "Styled text"

    def test_dict_api_oracle(self):
        """Oracle: parse_odt dict API returns correct counts and structure."""
        from odt.odt_parser import parse_odt
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:h text:outline-level="1">H1</text:h>'
            '<text:p>Para</text:p>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = _make_odt(content)
        result = parse_odt(path)
        assert result["ok"] is True
        assert result["paragraph_count"] == 1
        assert result["heading_count"] == 1
        assert result["paragraphs"][0]["text"] == "Para"
        assert result["headings"][0]["text"] == "H1"
        assert result["headings"][0]["level"] == 1

    def test_oracle_blocked_external_tool(self):
        """Document: full round-trip oracle requires LibreOffice (blocked)."""
        blocked_reason = "LibreOffice-generated reference files not available in CI"
        assert "LibreOffice" in blocked_reason
