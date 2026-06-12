"""Gate 5 neutral model and API hardening tests for ODS parser."""

import sys
import tempfile
import zipfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from ods.ods_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    OdsInvalidContainerError,
    get_capabilities,
    parse_ods,
    parse_ods_strict,
    probe_ods,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ods"


class TestOdsCapabilities:
    """Verify Gate 5 capability declarations."""

    def test_get_capabilities_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps["format"] == "ods"
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

    def test_formulas_explicitly_unsupported(self):
        assert "formulas" in UNSUPPORTED_FEATURES
        assert "formula_evaluation" in UNSUPPORTED_FEATURES

    def test_macros_explicitly_unsupported(self):
        assert "macros" in UNSUPPORTED_FEATURES

    def test_encryption_explicitly_unsupported(self):
        assert "encryption" in UNSUPPORTED_FEATURES

    def test_limits_in_capabilities(self):
        caps = get_capabilities()
        assert caps["max_file_size"] == 64 * 1024 * 1024
        assert caps["max_zip_entries"] == 1000
        assert caps["max_columns"] == 1024
        assert caps["max_rows"] == 1048576


class TestOdsEdgeCases:
    """Edge-case tests for Gate 5 hardening."""

    def _make_ods(self, content_xml: str) -> Path:
        """Create a minimal ODS file with custom content.xml."""
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            zf.writestr("content.xml", content_xml)
        return Path(tmp.name)

    def test_empty_spreadsheet(self):
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="Empty">'
            '</table:table>'
            '</office:spreadsheet></office:body>'
            '</office:document-content>'
        )
        path = self._make_ods(content)
        doc = parse_ods_strict(path)
        assert len(doc.sheets) == 1
        assert doc.sheets[0].name == "Empty"
        assert len(doc.sheets[0].rows) == 0

    def test_multiple_sheets(self):
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="Sheet1"></table:table>'
            '<table:table table:name="Sheet2"></table:table>'
            '<table:table table:name="Sheet3"></table:table>'
            '</office:spreadsheet></office:body>'
            '</office:document-content>'
        )
        path = self._make_ods(content)
        doc = parse_ods_strict(path)
        assert len(doc.sheets) == 3
        assert [s.name for s in doc.sheets] == ["Sheet1", "Sheet2", "Sheet3"]

    def test_missing_body_returns_empty(self):
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">'
            '</office:document-content>'
        )
        path = self._make_ods(content)
        doc = parse_ods_strict(path)
        assert len(doc.sheets) == 0

    def test_wrong_mimetype_raises(self):
        import pytest
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/pdf")
            zf.writestr("content.xml", "<x/>")
        with pytest.raises(OdsInvalidContainerError, match="Invalid mimetype"):
            parse_ods_strict(tmp.name)

    def test_missing_content_xml_raises(self):
        import pytest
        tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
        with zipfile.ZipFile(tmp.name, "w") as zf:
            zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        with pytest.raises(OdsInvalidContainerError, match="content.xml"):
            parse_ods_strict(tmp.name)

    def test_parse_ods_dict_error_has_error_type(self):
        result = parse_ods("/nonexistent/fake.ods")
        assert result["ok"] is False
        assert "error_type" in result

    def test_probe_returns_entries_list(self):
        result = probe_ods(SAMPLES / "valid" / "minimal-spreadsheet.ods")
        assert "entries" in result
        assert isinstance(result["entries"], list)
        assert "mimetype" in result["entries"]
