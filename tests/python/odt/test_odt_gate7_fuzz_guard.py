"""Gate 7 security and fuzz guard tests for ODT parser.

Deterministic malformed input guards. No heavy fuzzing.
"""

import sys
import tempfile
import zipfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pytest
from odt.odt_parser import (
    OdtError,
    OdtInvalidContainerError,
    OdtSizeError,
    parse_odt,
    parse_odt_strict,
)


class TestOdtFuzzGuards:
    """Malformed input guards for ODT parser."""

    def test_not_a_zip_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        tmp.write(b"Not a ZIP.")
        tmp.close()
        with pytest.raises(OdtInvalidContainerError):
            parse_odt_strict(tmp.name)

    def test_empty_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        tmp.close()
        with pytest.raises((OdtInvalidContainerError, OdtError)):
            parse_odt_strict(tmp.name)

    def test_zip_bomb_entry_count(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", "<x/>")
            for i in range(1001):
                zf.writestr(f"extra/{i}.txt", "x")
        with pytest.raises(OdtSizeError, match="entries"):
            parse_odt_strict(tmp.name)

    def test_malformed_xml_content(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", "<broken>><<")
        result = parse_odt(tmp.name)
        assert result["ok"] is False

    def test_binary_garbage_content_xml(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", bytes(range(256)))
        result = parse_odt(tmp.name)
        assert result["ok"] is False

    def test_dict_api_never_raises(self):
        result = parse_odt("/nonexistent")
        assert isinstance(result, dict)
        assert result["ok"] is False

    def test_extremely_nested_xml(self):
        depth = 100
        open_tags = "".join(f'<a xmlns:a="http://x/{i}">' for i in range(depth))
        close_tags = "</a>" * depth
        content = f'<?xml version="1.0"?>{open_tags}text{close_tags}'
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", content)
        result = parse_odt(tmp.name)
        assert isinstance(result, dict)

    def test_path_traversal_in_zip_entry(self):
        """Fuzz guard: ZIP entry with path-traversal name must not crash."""
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", '<x/>')
            zf.writestr("../../etc/passwd", "root:x:0:0")
        # Parser should not crash; it may raise or return error dict
        result = parse_odt(tmp.name)
        assert isinstance(result, dict)

    def test_missing_styles_xml_graceful(self):
        """Fuzz guard: ODT without styles.xml parses gracefully."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:p>No styles.xml present</text:p>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", content)
            # No styles.xml added
        result = parse_odt(tmp.name)
        assert result["ok"] is True
        assert result["paragraph_count"] == 1

    def test_xml_with_processing_instructions(self):
        """Fuzz guard: XML with processing instructions must not crash."""
        content = (
            '<?xml version="1.0"?>'
            '<?xml-stylesheet type="text/xsl" href="evil.xsl"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:p>PI test</text:p>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", content)
        result = parse_odt(tmp.name)
        assert isinstance(result, dict)
        # Should parse OK — PIs are harmless to ElementTree
        if result["ok"]:
            assert result["paragraph_count"] >= 1

    def test_deeply_nested_odf_elements(self):
        """Fuzz guard: deeply nested ODF text elements do not cause stack overflow."""
        depth = 200
        # Nested text:section elements (unsupported but valid ODF)
        open_tags = '<text:section text:name="s">' * depth
        close_tags = '</text:section>' * depth
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            f'{open_tags}<text:p>Deep</text:p>{close_tags}'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", content)
        result = parse_odt(tmp.name)
        assert isinstance(result, dict)

    def test_invalid_mimetype_content(self):
        """Fuzz guard: wrong mimetype content triggers container validation error."""
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/pdf")
            zf.writestr("content.xml", "<x/>")
        with pytest.raises(OdtInvalidContainerError, match="Invalid mimetype"):
            parse_odt_strict(tmp.name)

    def test_null_bytes_in_content_xml(self):
        """Fuzz guard: null bytes in content.xml handled gracefully."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:p>Before\x00After</text:p>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", content)
        result = parse_odt(tmp.name)
        assert isinstance(result, dict)

    def test_missing_content_xml(self):
        """Fuzz guard: ZIP with mimetype but no content.xml raises container error."""
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        with pytest.raises(OdtInvalidContainerError, match="content.xml"):
            parse_odt_strict(tmp.name)
