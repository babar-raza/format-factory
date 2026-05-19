"""Gate 7 security and fuzz guard tests for ODS parser.

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
from ods.ods_parser import (
    OdsError,
    OdsInvalidContainerError,
    OdsSizeError,
    parse_ods,
    parse_ods_strict,
)


class TestOdsFuzzGuards:
    """Malformed input guards for ODS parser."""

    def test_not_a_zip_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        tmp.write(b"This is not a ZIP file at all.")
        tmp.close()
        with pytest.raises(OdsInvalidContainerError):
            parse_ods_strict(tmp.name)

    def test_empty_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        tmp.close()
        with pytest.raises((OdsInvalidContainerError, OdsError)):
            parse_ods_strict(tmp.name)

    def test_zip_bomb_entry_count(self):
        """ZIP with too many entries should be rejected."""
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", "<x/>")
            for i in range(1001):
                zf.writestr(f"extra/{i}.txt", "x")
        with pytest.raises(OdsSizeError, match="entries"):
            parse_ods_strict(tmp.name)

    def test_malformed_xml_content(self):
        """Malformed XML in content.xml should fail gracefully."""
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", "<not-closed")
        result = parse_ods(tmp.name)
        assert result["ok"] is False

    def test_binary_garbage_content_xml(self):
        """Binary garbage in content.xml should fail gracefully."""
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", bytes(range(256)))
        result = parse_ods(tmp.name)
        assert result["ok"] is False

    def test_dict_api_never_raises(self):
        """parse_ods must never raise — always returns dict."""
        result = parse_ods("/nonexistent")
        assert isinstance(result, dict)
        assert result["ok"] is False

    def test_extremely_nested_xml(self):
        """Deeply nested XML should not cause stack overflow."""
        depth = 100
        open_tags = "".join(f'<a xmlns:a="http://x/{i}">' for i in range(depth))
        close_tags = "</a>" * depth
        content = f'<?xml version="1.0"?>{open_tags}text{close_tags}'
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", content)
        # Should not crash — may return empty sheets
        result = parse_ods(tmp.name)
        assert isinstance(result, dict)

    def test_path_traversal_in_zip_entry(self):
        """ZIP entry with path traversal (../../) must not cause file-system escape."""
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", (
                '<?xml version="1.0"?>'
                '<office:document-content '
                'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
                'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
                'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
                '<office:body><office:spreadsheet>'
                '<table:table table:name="Safe"/>'
                '</office:spreadsheet></office:body>'
                '</office:document-content>'
            ))
            # Malicious entry with path traversal
            zf.writestr("../../etc/passwd", "root:x:0:0:root:/root:/bin/bash")
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        tmp.write(buf.getvalue())
        tmp.close()
        # Parser should still work (it only reads mimetype + content.xml)
        # It must NOT extract or follow traversal paths
        result = parse_ods(tmp.name)
        assert isinstance(result, dict)
        # Verify no file was written outside
        import os
        assert not os.path.exists(os.path.join(os.path.dirname(tmp.name), "..", "..", "etc", "passwd"))

    def test_oversized_column_repeat_guard(self):
        """Column repeat exceeding MAX_COLUMNS must be clamped, not OOM."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="BigCol">'
            '<table:table-row>'
            '<table:table-cell office:value-type="string" '
            'table:number-columns-repeated="999999999">'
            '<text:p>X</text:p>'
            '</table:table-cell>'
            '</table:table-row>'
            '</table:table>'
            '</office:spreadsheet></office:body>'
            '</office:document-content>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", content)
        # Should not OOM — columns clamped to MAX_COLUMNS (1024)
        doc = parse_ods_strict(tmp.name)
        assert len(doc.sheets[0].rows[0].cells) <= 1024

    def test_missing_styles_xml_graceful(self):
        """ODS without styles.xml should parse gracefully (styles.xml is optional for parsing)."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="NoStyles">'
            '<table:table-row>'
            '<table:table-cell office:value-type="string"><text:p>OK</text:p></table:table-cell>'
            '</table:table-row>'
            '</table:table>'
            '</office:spreadsheet></office:body>'
            '</office:document-content>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", content)
            # No styles.xml, no meta.xml — just mimetype + content.xml
        doc = parse_ods_strict(tmp.name)
        assert doc.sheets[0].rows[0].cells[0].text == "OK"

    def test_xml_with_invalid_namespace(self):
        """content.xml with wrong namespace should return empty sheets, not crash."""
        content = (
            '<?xml version="1.0"?>'
            '<root xmlns:wrong="http://example.com/wrong">'
            '<wrong:table wrong:name="Bad"/>'
            '</root>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", content)
        doc = parse_ods_strict(tmp.name)
        assert len(doc.sheets) == 0

    def test_double_encoded_zip_rejected(self):
        """A ZIP-inside-a-ZIP must not parse as valid ODS."""
        import io
        # Create inner valid ODS
        inner = io.BytesIO()
        with zipfile.ZipFile(inner, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", "<x/>")
        inner_bytes = inner.getvalue()
        # Wrap in outer ZIP
        outer = io.BytesIO()
        with zipfile.ZipFile(outer, "w") as zf:
            zf.writestr("inner.ods", inner_bytes)
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        tmp.write(outer.getvalue())
        tmp.close()
        # Outer ZIP lacks mimetype entry — should fail container validation
        with pytest.raises((OdsInvalidContainerError, OdsError)):
            parse_ods_strict(tmp.name)

    def test_oversized_row_repeat_guard(self):
        """Row repeat exceeding MAX_ROWS must be clamped, not OOM."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="BigRow">'
            '<table:table-row table:number-rows-repeated="999999999">'
            '<table:table-cell office:value-type="string">'
            '<text:p>Y</text:p>'
            '</table:table-cell>'
            '</table:table-row>'
            '</table:table>'
            '</office:spreadsheet></office:body>'
            '</office:document-content>'
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", content)
        # Should not OOM — rows clamped to MAX_ROWS (1048576)
        doc = parse_ods_strict(tmp.name)
        assert len(doc.sheets[0].rows) <= 1048576
