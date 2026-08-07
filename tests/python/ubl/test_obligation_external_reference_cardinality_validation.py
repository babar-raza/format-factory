"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 -- cardinality validation, extended to ExternalReference.

MUST (SAL-UBL-OBL-03AF3A7D3A76F362 and its cross-capability duplicates):
"UBL document schemas are W3C XML Schema definitions and conforming
documents must be valid against the maindoc schema of their declared
type."

This extends the cardinality-validation slice (already proven for
cac:Party/cac:PostalAddress/cac:Contact/cac:PaymentMeans/
cac:PayeeFinancialAccount/cac:CreditNoteLine/cac:Response/
cac:DocumentReference/cac:InvoiceLine/cac:TaxSubtotal/cac:TaxTotal/
cac:LegalMonetaryTotal) to cac:ExternalReference. Every field's exact
cardinality is read directly from the pinned OASIS UBL 2.3
CommonAggregateComponents schema's ExternalReferenceType complexType.

Unlike every prior component in this cluster, cac:ExternalReference is not
currently reachable through this package's own typed document-parsing
path: it is a child of cac:Attachment, which model/reference.py does not
itself wire into any parent projector (cac:Attachment is not modeled by
this package at all). The cardinality check operates on the raw parsed
XML tree directly (UblDocument.root.iter()), not on typed projections, so
it still fires correctly for any real document containing a literal
cac:ExternalReference element -- this is genuine, spec-grounded validation
independent of the current typed-model's reach, honestly documented as
such rather than silently assumed equivalent to the cluster's other,
already-wired components.

cbc:Description is deliberately excluded, matching the established
"exclude genuinely repeatable fields" discipline: ExternalReferenceType
declares it minOccurs=0 maxOccurs=UNBOUNDED, unlike its sibling fields
URI/DocumentHash/MimeCode/FileName (all maxOccurs=1).
"""

from __future__ import annotations

from format_factory.ubl import loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice_with(body: str) -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"{body}"
        f"</Invoice>"
    ).encode()


def _document_reference_with_external_reference(external_reference_body: str) -> str:
    return (
        "<cac:AdditionalDocumentReference><cbc:ID>D1</cbc:ID>"
        "<cac:Attachment>"
        f"<cac:ExternalReference>{external_reference_body}</cac:ExternalReference>"
        "</cac:Attachment></cac:AdditionalDocumentReference>"
    )


def test_an_external_reference_with_one_of_each_field_validates_cleanly() -> None:
    body = _document_reference_with_external_reference(
        "<cbc:URI>http://example.com/doc.pdf</cbc:URI>"
        "<cbc:DocumentHash>abc123</cbc:DocumentHash>"
        "<cbc:MimeCode>application/pdf</cbc:MimeCode>"
        "<cbc:FileName>doc.pdf</cbc:FileName>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_an_external_reference_with_two_uris_is_a_cardinality_violation() -> None:
    body = _document_reference_with_external_reference(
        "<cbc:URI>http://example.com/a.pdf</cbc:URI><cbc:URI>http://example.com/b.pdf</cbc:URI>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_an_external_reference_with_two_document_hashes_is_a_cardinality_violation() -> None:
    body = _document_reference_with_external_reference(
        "<cbc:DocumentHash>abc</cbc:DocumentHash><cbc:DocumentHash>def</cbc:DocumentHash>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_an_external_reference_with_two_mime_codes_is_a_cardinality_violation() -> None:
    body = _document_reference_with_external_reference(
        "<cbc:MimeCode>application/pdf</cbc:MimeCode><cbc:MimeCode>image/png</cbc:MimeCode>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_an_external_reference_with_two_file_names_is_a_cardinality_violation() -> None:
    body = _document_reference_with_external_reference(
        "<cbc:FileName>a.pdf</cbc:FileName><cbc:FileName>b.pdf</cbc:FileName>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_multiple_descriptions_are_not_a_violation_the_schema_declares_them_repeatable() -> None:
    """ExternalReferenceType declares cbc:Description minOccurs=0
    maxOccurs=UNBOUNDED -- genuinely repeatable, confirmed directly against
    the pinned schema rather than assumed uniform with its sibling fields."""
    body = _document_reference_with_external_reference(
        "<cbc:Description>English description</cbc:Description>"
        "<cbc:Description>Description in another language</cbc:Description>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True
