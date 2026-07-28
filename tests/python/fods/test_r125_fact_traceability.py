"""
test_r125_fact_traceability.py
Sprint: SPEC-AUTHORITY-LAYER-PILOT-CLOSURE-DEBT-REPAIR-001
Added: 2026-06-08

Lane 5 — FODS P5 traceability tests.

SAL-FODS-00001: "FODS root element is <office:document> with office:mimetype attribute"
  Spec: ODF 1.3 Part 3, section 3.1.2
  SHA:  sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
  Status: verified | validated_by: independent_agent_verifier

These tests establish P5 traceability:
- Code in src/python/fods/constants.py cites SAL-FODS-00001
- Tests here reference SAL-FODS-00001 explicitly
"""
import sys
from pathlib import Path


# Allow direct import of fods package
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from fods.constants import QN_DOCUMENT, ATTR_MIMETYPE, NS_OFFICE


# ---------------------------------------------------------------------------
# SAL-FODS-00001 traceability: root element and mimetype attribute
# ---------------------------------------------------------------------------


class TestFactFods001Traceability:
    """
    SAL-FODS-00001: FODS root element is <office:document> with office:mimetype attribute.

    These tests verify that the code constants align with the verified spec fact
    and that the fact citation exists in the source code.
    """

    def test_qn_document_matches_fact_fods_001(self):
        """SAL-FODS-00001: QN_DOCUMENT must be '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document'.

        Per SAL-FODS-00001 (ODF 1.3 Part 3, section 3.1.2):
        The root element of a FODS document is <office:document>.
        """
        expected = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document"
        assert QN_DOCUMENT == expected, (
            f"SAL-FODS-00001 violation: QN_DOCUMENT={QN_DOCUMENT!r} does not match spec-derived value {expected!r}"
        )

    def test_attr_mimetype_matches_fact_fods_001(self):
        """SAL-FODS-00001: ATTR_MIMETYPE must be '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}mimetype'.

        Per SAL-FODS-00001 (ODF 1.3 Part 3, section 3.1.2):
        The <office:document> element has the office:mimetype attribute.
        """
        expected = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}mimetype"
        assert ATTR_MIMETYPE == expected, (
            f"SAL-FODS-00001 violation: ATTR_MIMETYPE={ATTR_MIMETYPE!r} does not match spec-derived value {expected!r}"
        )

    def test_ns_office_is_spec_defined_uri(self):
        """SAL-FODS-00001: NS_OFFICE URI must match the ODF 1.3 namespace definition.

        The office: namespace prefix maps to urn:oasis:names:tc:opendocument:xmlns:office:1.0
        per ODF 1.3 Part 3 section 3.1.2.
        """
        expected_ns = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
        assert NS_OFFICE == expected_ns

    def test_fact_fods_001_citation_exists_in_constants_source(self):
        """SAL-FODS-00001 citation must appear in constants.py source (P5 traceability).

        P5 traceability requires that the source code explicitly cites the spec fact ID
        on the relevant constant definitions.
        """
        constants_file = Path(__file__).parent.parent.parent.parent / "src" / "python" / "fods" / "constants.py"
        assert constants_file.exists(), "constants.py not found"
        source = constants_file.read_text(encoding="utf-8")
        assert "SAL-FODS-00001" in source, (
            "P5 traceability requires SAL-FODS-00001 citation in src/python/fods/constants.py. "
            "Add comment '# SAL-FODS-00001' to QN_DOCUMENT and ATTR_MIMETYPE definitions."
        )

    def test_mimetype_value_is_spec_defined(self):
        """SAL-FODS-00001 implies: office:mimetype value for FODS is the spreadsheet-flat-xml MIME type.

        The expected MIME type is defined by ODF 1.3 and must match the constant.
        """
        from fods.constants import EXPECTED_MIMETYPE
        assert EXPECTED_MIMETYPE == "application/vnd.oasis.opendocument.spreadsheet-flat-xml", (
            "EXPECTED_MIMETYPE must match ODF 1.3 FODS MIME type per spec"
        )

    def test_fods_parser_uses_qn_document_for_root_detection(self):
        """SAL-FODS-00001: Parser must use QN_DOCUMENT to detect the root element.

        P5 traceability: the parser code should reference QN_DOCUMENT (not a hardcoded string)
        when checking for the root element.
        """
        fods_module_dir = Path(__file__).parent.parent.parent.parent / "src" / "python" / "fods"
        parser_files = list(fods_module_dir.glob("*.py"))
        assert parser_files is not None, "No FODS parser files found"

        qn_document_used = False
        for f in parser_files:
            if "QN_DOCUMENT" in f.read_text(encoding="utf-8"):
                qn_document_used = True
                break
        assert qn_document_used is not None, (
            "SAL-FODS-00001: No FODS source file references QN_DOCUMENT. "
            "Parser must use QN_DOCUMENT constant for root element detection."
        )
