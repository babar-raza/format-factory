"""UBL-CODELIST-001 -- cac:ExternalReference (SAL-UBL-OBL-88EBC13520652DAE).

MUST, quoted from the format contract:

  "cac:ExternalReference is an aggregate with optional URI, DocumentHash,
   MimeCode, FileName, and Description elements."

Every element is optional per the spec (SAL-UBL-00119, verified against
the OASIS UBL Specification) -- this file tests exactly that: every field
absent is valid, every field present round-trips, and no field is
invented as required.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import ExternalReference, UblValidationError, XmlNode, external_reference_of

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _child(local: str, text: str) -> XmlNode:
    return XmlNode.create(f"{{{_CBC}}}{local}", text=text)


class TestExternalReferenceConstruction:
    def test_all_fields_default_to_none(self) -> None:
        ref = ExternalReference()
        assert ref.uri is None
        assert ref.document_hash is None
        assert ref.mime_code is None
        assert ref.filename is None
        assert ref.description is None

    def test_every_field_is_independently_settable(self) -> None:
        ref = ExternalReference(
            uri="http://example.com/doc.pdf",
            document_hash="deadbeef",
            mime_code="application/pdf",
            filename="doc.pdf",
            description="An invoice attachment",
        )
        assert ref.uri == "http://example.com/doc.pdf"
        assert ref.document_hash == "deadbeef"
        assert ref.mime_code == "application/pdf"
        assert ref.filename == "doc.pdf"
        assert ref.description == "An invoice attachment"

    def test_is_frozen(self) -> None:
        ref = ExternalReference(uri="http://example.com")
        with pytest.raises(Exception):
            ref.uri = "http://other.example.com"  # type: ignore[misc]


class TestExternalReferenceProjection:
    def test_projecting_an_empty_element_yields_all_none(self) -> None:
        node = XmlNode.create(f"{{{_CAC}}}ExternalReference")
        ref = external_reference_of(node)
        assert ref == ExternalReference()

    def test_projecting_a_full_element(self) -> None:
        node = XmlNode.create(
            f"{{{_CAC}}}ExternalReference",
            children=(
                _child("URI", "http://example.com/doc.pdf"),
                _child("DocumentHash", "deadbeef"),
                _child("MimeCode", "application/pdf"),
                _child("FileName", "doc.pdf"),
                _child("Description", "An invoice attachment"),
            ),
        )
        ref = external_reference_of(node)
        assert ref.uri == "http://example.com/doc.pdf"
        assert ref.document_hash == "deadbeef"
        assert ref.mime_code == "application/pdf"
        assert ref.filename == "doc.pdf"
        assert ref.description == "An invoice attachment"

    def test_projecting_a_partial_element_leaves_the_rest_none(self) -> None:
        node = XmlNode.create(
            f"{{{_CAC}}}ExternalReference",
            children=(_child("URI", "http://example.com/doc.pdf"),),
        )
        ref = external_reference_of(node)
        assert ref.uri == "http://example.com/doc.pdf"
        assert ref.document_hash is None
        assert ref.mime_code is None
        assert ref.filename is None
        assert ref.description is None

    def test_projecting_a_missing_element_is_refused(self) -> None:
        with pytest.raises(UblValidationError):
            external_reference_of(None)
