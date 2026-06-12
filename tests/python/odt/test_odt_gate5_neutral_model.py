"""Gate 5 neutral model and API hardening tests for ODT parser."""

import sys
import tempfile
import zipfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from odt.odt_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    OdtHeading,
    OdtInvalidContainerError,
    OdtParagraph,
    get_capabilities,
    parse_odt,
    parse_odt_strict,
    probe_odt,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "odt"


class TestOdtCapabilities:
    """Verify Gate 5 capability declarations."""

    def test_get_capabilities_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps["format"] == "odt"
        assert caps["gate"] == 5

    def test_commercial_product_ready_false(self):
        caps = get_capabilities()
        assert caps["commercial_product_ready"] is False

    def test_supported_features_nonempty(self):
        assert len(SUPPORTED_FEATURES) > 0
        caps = get_capabilities()
        assert len(caps["supported"]) == len(SUPPORTED_FEATURES)

    def test_unsupported_features_nonempty(self):
        assert len(UNSUPPORTED_FEATURES) > 0
        caps = get_capabilities()
        assert len(caps["unsupported"]) == len(UNSUPPORTED_FEATURES)

    def test_no_overlap_supported_unsupported(self):
        overlap = SUPPORTED_FEATURES & UNSUPPORTED_FEATURES
        assert len(overlap) == 0, f"Overlap: {overlap}"

    def test_tables_explicitly_unsupported(self):
        assert "tables" in UNSUPPORTED_FEATURES

    def test_images_explicitly_unsupported(self):
        assert "images" in UNSUPPORTED_FEATURES

    def test_macros_explicitly_unsupported(self):
        assert "macros" in UNSUPPORTED_FEATURES

    def test_encryption_explicitly_unsupported(self):
        assert "encryption" in UNSUPPORTED_FEATURES

    def test_limits_in_capabilities(self):
        caps = get_capabilities()
        assert caps["max_file_size"] == 64 * 1024 * 1024
        assert caps["max_zip_entries"] == 1000


class TestOdtEdgeCases:
    """Edge-case tests for Gate 5 hardening."""

    def _make_odt(self, content_xml: str) -> Path:
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
            zf.writestr("content.xml", content_xml)
        return Path(tmp.name)

    def test_empty_document(self):
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = self._make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.paragraphs) == 0
        assert len(doc.headings) == 0
        assert len(doc.elements) == 0

    def test_heading_levels(self):
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:h text:outline-level="1">H1</text:h>'
            '<text:h text:outline-level="2">H2</text:h>'
            '<text:h text:outline-level="3">H3</text:h>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = self._make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.headings) == 3
        assert doc.headings[0].level == 1
        assert doc.headings[1].level == 2
        assert doc.headings[2].level == 3

    def test_mixed_paragraphs_and_headings(self):
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:text>'
            '<text:h text:outline-level="1">Title</text:h>'
            '<text:p>Para 1</text:p>'
            '<text:p>Para 2</text:p>'
            '</office:text></office:body>'
            '</office:document-content>'
        )
        path = self._make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.elements) == 3
        assert isinstance(doc.elements[0], OdtHeading)
        assert isinstance(doc.elements[1], OdtParagraph)
        assert isinstance(doc.elements[2], OdtParagraph)

    def test_missing_body_returns_empty(self):
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">'
            '</office:document-content>'
        )
        path = self._make_odt(content)
        doc = parse_odt_strict(path)
        assert len(doc.paragraphs) == 0

    def test_wrong_mimetype_raises(self):
        import pytest
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/pdf")
            zf.writestr("content.xml", "<x/>")
        with pytest.raises(OdtInvalidContainerError, match="Invalid mimetype"):
            parse_odt_strict(tmp.name)

    def test_missing_content_xml_raises(self):
        import pytest
        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        with pytest.raises(OdtInvalidContainerError, match="content.xml"):
            parse_odt_strict(tmp.name)

    def test_parse_odt_dict_error_has_error_type(self):
        result = parse_odt("/nonexistent/fake.odt")
        assert result["ok"] is False
        assert "error_type" in result

    def test_probe_returns_entries_list(self):
        result = probe_odt(SAMPLES / "valid" / "minimal-document.odt")
        assert "entries" in result
        assert isinstance(result["entries"], list)
