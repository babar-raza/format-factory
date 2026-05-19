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
