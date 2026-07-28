"""Tests for fodp.get_document_metadata — ODF document-level metadata extraction.

Spec authority: ODF 1.3, section 4 (SAL-FODP-00103, SAL-FODP-00107, SAL-FODP-00109).
Gap: GAP-FODP-CODEC-DEBT (codec_quality, foss_reduced)
"""
import sys
from pathlib import Path

import pytest

# Load fodp_codec directly from source tree to avoid stale installed package.
# Imported as a real `fodp.fodp_codec` submodule (not via spec_from_file_location
# as a detached top-level module) so its `from .exceptions import ...` relative
# import resolves correctly; inserting src/python at the front of sys.path still
# guarantees the source tree wins over any installed package.
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import fodp_codec as _mod
get_document_metadata = _mod.get_document_metadata
FodpParseError = _mod.FodpParseError


# --- Fixtures: minimal FODP XML strings ---

FODP_WITH_FULL_META = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:meta>
    <dc:title>Test Presentation</dc:title>
    <dc:description>A test description</dc:description>
    <dc:subject>Testing</dc:subject>
    <dc:creator>Unit Tester</dc:creator>
    <dc:date>2026-06-24T12:00:00</dc:date>
    <dc:language>en-US</dc:language>
    <meta:creation-date>2026-06-20T08:00:00</meta:creation-date>
    <meta:generator>format-factory-test/1.0</meta:generator>
    <meta:editing-cycles>5</meta:editing-cycles>
    <meta:editing-duration>PT2H30M</meta:editing-duration>
    <meta:initial-creator>Original Author</meta:initial-creator>
  </office:meta>
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1"/>
    </office:presentation>
  </office:body>
</office:document>
"""

FODP_WITH_PARTIAL_META = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:meta>
    <dc:title>Only Title</dc:title>
    <meta:generator>LibreOffice/7.4</meta:generator>
  </office:meta>
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1"/>
    </office:presentation>
  </office:body>
</office:document>
"""

FODP_WITHOUT_META = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">
  <office:body>
    <office:presentation>
      <draw:page draw:name="Slide1"/>
    </office:presentation>
  </office:body>
</office:document>
"""


class TestGetDocumentMetadataFullMeta:
    """Test extraction when all pre-defined metadata elements are present."""

    def test_returns_dict(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert isinstance(result, dict)

    def test_title(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["title"] == "Test Presentation"

    def test_description(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["description"] == "A test description"

    def test_creator(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["creator"] == "Unit Tester"

    def test_generator(self):
        """SAL-FODP-00109: meta:generator identifies the producer."""
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["generator"] == "format-factory-test/1.0"

    def test_creation_date(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["creation_date"] == "2026-06-20T08:00:00"

    def test_date(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["date"] == "2026-06-24T12:00:00"

    def test_subject(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["subject"] == "Testing"

    def test_language(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["language"] == "en-US"

    def test_editing_cycles(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["editing_cycles"] == "5"

    def test_editing_duration(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["editing_duration"] == "PT2H30M"

    def test_initial_creator(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        assert result["initial_creator"] == "Original Author"

    def test_all_keys_present(self):
        result = get_document_metadata(FODP_WITH_FULL_META)
        expected_keys = {
            "title", "description", "subject", "creator", "date",
            "language", "creation_date", "generator", "editing_cycles",
            "editing_duration", "initial_creator",
        }
        assert set(result.keys()) == expected_keys


class TestGetDocumentMetadataPartialMeta:
    """Test with only some metadata elements present."""

    def test_title_present(self):
        result = get_document_metadata(FODP_WITH_PARTIAL_META)
        assert result["title"] == "Only Title"

    def test_generator_present(self):
        result = get_document_metadata(FODP_WITH_PARTIAL_META)
        assert result["generator"] == "LibreOffice/7.4"

    def test_missing_fields_are_none(self):
        result = get_document_metadata(FODP_WITH_PARTIAL_META)
        assert result["description"] is None
        assert result["creator"] is None
        assert result["date"] is None
        assert result["subject"] is None
        assert result["creation_date"] is None
        assert result["editing_cycles"] is None


class TestGetDocumentMetadataNoMetaElement:
    """Test when <office:meta> element is absent entirely."""

    def test_all_fields_none(self):
        result = get_document_metadata(FODP_WITHOUT_META)
        for key, value in result.items():
            assert value is None, f"Expected None for {key!r}, got {value!r}"

    def test_returns_correct_key_count(self):
        result = get_document_metadata(FODP_WITHOUT_META)
        assert len(result) == 11


class TestGetDocumentMetadataFromBytes:
    """Test that bytes input works correctly."""

    def test_bytes_input(self):
        result = get_document_metadata(FODP_WITH_FULL_META.encode("utf-8"))
        assert result["title"] == "Test Presentation"


class TestGetDocumentMetadataSpecQname:
    """Verify spec_qname attribute is set on the function."""

    def test_has_spec_qname(self):
        assert hasattr(get_document_metadata, "spec_qname")
        assert get_document_metadata.spec_qname == "office:meta"


class TestGetDocumentMetadataErrorHandling:
    """Test error cases."""

    def test_invalid_xml_raises(self):
        with pytest.raises(FodpParseError):
            get_document_metadata("<not valid xml>>>")

    def test_wrong_root_raises(self):
        bad_xml = '<html xmlns="http://www.w3.org/1999/xhtml"><body/></html>'
        with pytest.raises(FodpParseError, match="Root element must be office:document"):
            get_document_metadata(bad_xml)
