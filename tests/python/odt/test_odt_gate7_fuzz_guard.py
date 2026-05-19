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
